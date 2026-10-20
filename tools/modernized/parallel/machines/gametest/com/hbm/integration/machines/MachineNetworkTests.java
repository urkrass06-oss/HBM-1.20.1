/* SPDX-License-Identifier: LGPL-3.0-only */
package com.hbm.integration.machines;

import com.hbm_m.api.energy.EnergyNetworkManager;
import com.hbm_m.api.energy.WireBlockEntity;
import com.hbm_m.api.fluids.FluidNet;
import com.hbm_m.api.fluids.FluidNetProvider;
import com.hbm_m.api.fluids.IFluidStandardTransceiverMK2;
import com.hbm_m.api.network.UniNodespace;
import com.hbm_m.block.ModBlocks;
import com.hbm_m.blockentity.machines.FluidPumpBlockEntity;
import com.hbm_m.blockentity.machines.FluidValveBlockEntity;
import com.hbm_m.blockentity.machines.MachineBatteryBlockEntity;
import com.hbm_m.capability.ModCapabilities;
import com.hbm_m.inventory.fluid.tank.FluidTank;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.minecraftforge.fluids.FluidStack;
import net.minecraftforge.fluids.capability.IFluidHandler.FluidAction;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

/** Independent behavioral fixtures. Fake lifecycle calls are tested separately from real unloads. */
@GameTestHolder("hbm_m")
@PrefixGameTestTemplate(false)
public final class MachineNetworkTests {
    @GameTest(template = "empty")
    public static void capabilitiesInvalidateOnRemoval(GameTestHelper h) {
        var wire = new WireBlockEntity(BlockPos.ZERO, ModBlocks.WIRE_COATED.get().defaultBlockState());
        var old = wire.getCapability(ModCapabilities.HBM_ENERGY_CONNECTOR);
        h.assertTrue(old.isPresent(), "New connector capability absent");
        wire.setRemoved();
        h.assertTrue(!old.isPresent(), "Removed connector capability still valid");
        wire.clearRemoved();
        wire.reviveCaps();
        var revived = wire.getCapability(ModCapabilities.HBM_ENERGY_CONNECTOR);
        h.assertTrue(revived.isPresent(), "Revived connector capability absent");
        h.assertTrue(!old.isPresent(), "Old capability became valid again");
        wire.invalidateCaps();
        h.assertTrue(!revived.isPresent(), "Second capability invalidation failed");
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void singletonNetworkCanReconnect(GameTestHelper h) {
        var a = h.absolutePos(new BlockPos(1, 2, 1));
        var b = a.east();
        var level = h.getLevel();
        level.setBlockAndUpdate(a, ModBlocks.WIRE_COATED.get().defaultBlockState());
        level.setBlockAndUpdate(b, ModBlocks.WIRE_COATED.get().defaultBlockState());
        var manager = EnergyNetworkManager.get(level);
        manager.addNode(a);
        manager.addNode(b);
        level.setBlockAndUpdate(b, Blocks.AIR.defaultBlockState());
        h.assertTrue(manager.getNode(a) != null && manager.getNode(a).getNetwork() != null,
                "Removing one of two nodes orphaned the surviving node");
        level.setBlockAndUpdate(b, ModBlocks.WIRE_COATED.get().defaultBlockState());
        manager.addNode(b);
        h.assertTrue(manager.getNode(a).getNetwork() == manager.getNode(b).getNetwork(),
                "Replaced neighbor did not reconnect to singleton");
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void valveUnloadReleasesNodeImmediately(GameTestHelper h) {
        var pos = h.absolutePos(new BlockPos(2, 2, 2));
        var level = h.getLevel();
        level.setBlockAndUpdate(pos, ModBlocks.FLUID_VALVE.get().defaultBlockState());
        var valve = (FluidValveBlockEntity) level.getBlockEntity(pos);
        valve.setFluidType(Fluids.WATER);
        var provider = FluidNetProvider.forFluid(Fluids.WATER);
        var node = UniNodespace.getNode(level, pos, provider);
        h.assertTrue(node != null, "Valve did not register a node");
        valve.onChunkUnloaded();
        h.assertTrue(UniNodespace.getNode(level, pos, provider) == null,
                "Valve unload left a cached node until the global reaper");
        h.assertTrue(node.isExpired(), "Unloaded valve node not expired");
        valve.onLoad();
        var fresh = UniNodespace.getNode(level, pos, provider);
        h.assertTrue(fresh != null && fresh != node && !fresh.isExpired(), "Valve did not rebuild a fresh node");
        h.succeed();
    }

    private static MachineBatteryBlockEntity battery(ServerLevel level, BlockPos pos, boolean output, long he) {
        level.setBlockAndUpdate(pos, ModBlocks.MACHINE_BATTERY_SCHRABIDIUM.get().defaultBlockState());
        var entity = (MachineBatteryBlockEntity) level.getBlockEntity(pos);
        entity.modeOnNoSignal = entity.modeOnSignal = output ? 2 : 1;
        entity.setEnergyStored(he);
        return entity;
    }

    private static FluidPumpBlockEntity pump(ServerLevel level, BlockPos pos, int amount) {
        level.setBlockAndUpdate(pos, ModBlocks.FLUID_PUMP.get().defaultBlockState());
        var entity = (FluidPumpBlockEntity) level.getBlockEntity(pos);
        entity.bufferSize = 18_000;
        entity.setFluidType(Fluids.WATER);
        entity.getAllTanks()[0].changeTankSize(18_000);
        entity.getAllTanks()[0].setFluid(Fluids.WATER, amount);
        entity.setChanged();
        return entity;
    }

    private static void portalTickets(ServerLevel level, BlockPos center) {
        // Vanilla portal tickets expire after 300 ticks. They provide initial ticking
        // without leaving a forced chunk or a test-owned permanent ticket behind.
        for (int dx : new int[]{-1, 0}) {
            var chunk = new ChunkPos(center.offset(dx, 0, 0));
            level.getChunkSource().addRegionTicket(TicketType.PORTAL, chunk, 3, center);
        }
    }

    private static void arena(ServerLevel level, BlockPos center, long he, int mb) {
        portalTickets(level, center);
        clear(level, center);
        battery(level, center.east(), true, he);
        battery(level, center.west(), false, 0);
        level.setBlockAndUpdate(center, ModBlocks.WIRE_COATED.get().defaultBlockState());
        var pipe = center.south(4);
        pump(level, pipe.east(), mb);
        pump(level, pipe.west(), 0);
        level.setBlockAndUpdate(pipe, ModBlocks.FLUID_VALVE.get().defaultBlockState());
        ((FluidValveBlockEntity) level.getBlockEntity(pipe)).setFluidType(Fluids.WATER);
    }

    private static void balance(GameTestHelper h, ServerLevel level, BlockPos center, long he, int mb) {
        var a = (MachineBatteryBlockEntity) level.getBlockEntity(center.east());
        var b = (MachineBatteryBlockEntity) level.getBlockEntity(center.west());
        var p = (FluidPumpBlockEntity) level.getBlockEntity(center.south(4).east());
        var q = (FluidPumpBlockEntity) level.getBlockEntity(center.south(4).west());
        h.assertTrue(a.getEnergyStored() + b.getEnergyStored() == he, "HE balance changed");
        h.assertTrue(p.getAllTanks()[0].getFill() + q.getAllTanks()[0].getFill() == mb,
                        "Fluid balance changed: source=" + p.getAllTanks()[0].getFill()
                        + ", target=" + q.getAllTanks()[0].getFill() + ", expected=" + mb);
    }

    private static void clear(ServerLevel level, BlockPos center) {
        for (int z : new int[]{0, 4}) for (int x = -1; x <= 1; x++)
            level.setBlockAndUpdate(center.offset(x, 0, z), Blocks.AIR.defaultBlockState());
    }

    private static void awaitUnload(GameTestHelper h, ServerLevel level, BlockPos center,
                                    int attempts, Runnable afterUnload) {
        if (!level.hasChunk(center.getX() >> 4, center.getZ() >> 4)
                && !level.hasChunk((center.getX() - 1) >> 4, center.getZ() >> 4)) {
            afterUnload.run();
            return;
        }
        h.assertTrue(attempts > 0, "Arena did not unload normally; this is not an unload proof: "
                + level.getChunkSource().getChunkDebugData(new ChunkPos(center)));
        h.runAfterDelay(20, () -> awaitUnload(h, level, center, attempts - 1, afterUnload));
    }

    private static void awaitFlow(GameTestHelper h, ServerLevel level, BlockPos center,
                                  int attempts, Runnable afterFlow) {
        balance(h, level, center, 20_000_000L, 18_000);
        var energy = (MachineBatteryBlockEntity) level.getBlockEntity(center.west());
        var fluid = (FluidPumpBlockEntity) level.getBlockEntity(center.south(4).west());
        if (energy.getEnergyStored() > 0 && fluid.getAllTanks()[0].getFill() > 0) {
            afterFlow.run();
            return;
        }
        h.assertTrue(attempts > 0, "Transfer never started before unload; HE=" + energy.getEnergyStored()
                + ", mB=" + fluid.getAllTanks()[0].getFill() + ", chunk="
                + level.getChunkSource().getChunkDebugData(new ChunkPos(center)));
        h.runAfterDelay(10, () -> awaitFlow(h, level, center, attempts - 1, afterFlow));
    }

    @GameTest(template = "empty", timeoutTicks = 200)
    public static void splitMergePreservesAmounts(GameTestHelper h) {
        var level = h.getLevel();
        var center = new BlockPos(160_208, 100, 160_208);
        arena(level, center, 20_000_000L, 18_000);
        h.runAfterDelay(20, () -> {
            balance(h, level, center, 20_000_000L, 18_000);
            level.setBlockAndUpdate(center, Blocks.AIR.defaultBlockState());
            var pipe = center.south(4);
            var valve = (FluidValveBlockEntity) level.getBlockEntity(pipe);
            level.setBlockAndUpdate(pipe.below(), Blocks.REDSTONE_BLOCK.defaultBlockState());
            valve.updateRedstone(level, pipe);
            h.assertTrue(!valve.isOpen(), "Powered valve stayed open");
            var a = (MachineBatteryBlockEntity) level.getBlockEntity(center.east());
            var b = (MachineBatteryBlockEntity) level.getBlockEntity(center.west());
            var p = (FluidPumpBlockEntity) level.getBlockEntity(pipe.east());
            var q = (FluidPumpBlockEntity) level.getBlockEntity(pipe.west());
            a.setEnergyStored(20_000_000L);
            b.setEnergyStored(0);
            p.getAllTanks()[0].drainMb(18_000);
            q.getAllTanks()[0].drainMb(18_000);
            p.getAllTanks()[0].fillMb(Fluids.WATER, 18_000);
            h.runAfterDelay(5, () -> {
                balance(h, level, center, 20_000_000L, 18_000);
                h.assertTrue(b.getEnergyStored() == 0 && q.getAllTanks()[0].getFill() == 0,
                        "Transfer continued across a split network");
                level.setBlockAndUpdate(center, ModBlocks.WIRE_COATED.get().defaultBlockState());
                level.setBlockAndUpdate(pipe.below(), Blocks.AIR.defaultBlockState());
                valve.updateRedstone(level, pipe);
                h.runAfterDelay(10, () -> {
                    balance(h, level, center, 20_000_000L, 18_000);
                    h.assertTrue(b.getEnergyStored() > 0,
                            "HE transfer did not resume after merging; stored=" + b.getEnergyStored());
                    h.assertTrue(q.getAllTanks()[0].getFill() > 0,
                            "Fluid transfer did not resume after merging; valveOpen=" + valve.isOpen());
                    var saved = p.saveWithFullMetadata();
                    var restored = new FluidPumpBlockEntity(p.getBlockPos(), p.getBlockState());
                    restored.load(saved);
                    h.assertTrue(restored.bufferSize == 18_000 && restored.getFluidType() == Fluids.WATER
                            && restored.getAllTanks()[0].getFill() == p.getAllTanks()[0].getFill(),
                            "Pump configuration or buffered fluid changed on NBT roundtrip");
                    clear(level, center);
                    h.succeed();
                });
            });
        });
    }

    @GameTest(template = "empty", timeoutTicks = 2200)
    public static void networkUnloadReloadConservesAmounts(GameTestHelper h) {
        // These chunks are outside GameTest's forced structure chunks and the spawn region.
        // Initial vanilla portal tickets expire; no setChunkForced/forcechunks call.
        var center = new BlockPos(160_016, 100, 160_016);
        var level = h.getLevel();
        arena(level, center, 20_000_000L, 18_000);
        h.runAfterDelay(30, () -> awaitFlow(h, level, center, 20, () -> {
            balance(h, level, center, 20_000_000L, 18_000);
            var wire = (WireBlockEntity) level.getBlockEntity(center);
            var old = wire.getCapability(ModCapabilities.HBM_ENERGY_CONNECTOR);
            h.runAfterDelay(400, () -> awaitUnload(h, level, center, 60, () -> {
                h.assertTrue(!old.isPresent(), "Unloaded wire retained capability");
                portalTickets(level, center);
                level.getChunk(center.getX() >> 4, center.getZ() >> 4);
                level.getChunk((center.getX() - 1) >> 4, center.getZ() >> 4);
                h.runAfterDelay(20, () -> {
                    balance(h, level, center, 20_000_000L, 18_000);
                    var restored = (WireBlockEntity) level.getBlockEntity(center);
                    h.assertTrue(restored != wire, "Chunk did not create a fresh block entity");
                    h.assertTrue(restored.getCapability(ModCapabilities.HBM_ENERGY_CONNECTOR).isPresent(),
                            "Reloaded connector capability absent");
                    var manager = EnergyNetworkManager.get(level);
                    h.assertTrue(manager.getNode(center) != null && manager.getNode(center).getNetwork() != null
                            && manager.getNode(center.east()).getNetwork() == manager.getNode(center.west()).getNetwork(),
                            "Reloaded energy graph did not reconnect");
                    var fluidNode = UniNodespace.getNode(level, center.south(4), FluidNetProvider.forFluid(Fluids.WATER));
                    h.assertTrue(fluidNode != null && fluidNode.net != null && !fluidNode.isExpired(),
                            "Reloaded valve did not rebuild its network");
                    clear(level, center);
                    h.succeed();
                });
            }));
        }));
    }

    @GameTest(template = "empty", timeoutTicks = 200)
    public static void networksAreDimensionLocal(GameTestHelper h) {
        var first = h.getLevel();
        var second = first.getServer().getLevel(Level.NETHER);
        h.assertTrue(second != null, "Nether unavailable");
        var center = new BlockPos(160_112, 100, 160_112);
        arena(first, center, 20_000_000L, 18_000);
        arena(second, center, 7_000_000L, 7_000);
        h.runAfterDelay(30, () -> {
            balance(h, first, center, 20_000_000L, 18_000);
            balance(h, second, center, 7_000_000L, 7_000);
            var a = EnergyNetworkManager.get(first);
            var b = EnergyNetworkManager.get(second);
            h.assertTrue(a != b && a.getNode(center).getNetwork() != b.getNode(center).getNetwork(),
                    "Energy networks crossed dimensions");
            var provider = FluidNetProvider.forFluid(Fluids.WATER);
            var x = UniNodespace.getNode(first, center.south(4), provider);
            var y = UniNodespace.getNode(second, center.south(4), provider);
            h.assertTrue(x != null && y != null && x.net != null && y.net != null && x.net != y.net,
                    "Fluid networks crossed dimensions");
            clear(first, center);
            clear(second, center);
            h.succeed();
        });
    }

    private static final class Endpoint implements IFluidStandardTransceiverMK2 {
        private final FluidTank tank;
        Endpoint(Fluid fluid, int pressure, int amount) {
            tank = new FluidTank(10_000);
            tank.conform(fluid, pressure);
            // Seed a process buffer directly: external Forge fill deliberately rejects pressure.
            tank.setFluid(fluid, amount);
        }
        @Override public FluidTank[] getAllTanks() { return new FluidTank[]{tank}; }
        @Override public FluidTank[] getSendingTanks() { return getAllTanks(); }
        @Override public FluidTank[] getReceivingTanks() { return getAllTanks(); }
        @Override public boolean canConnect(Fluid fluid, Direction side) { return true; }
        @Override public boolean isLoaded() { return true; }
    }

    @GameTest(template = "empty")
    public static void pressureAndSubstanceStaySeparate(GameTestHelper h) {
        for (int pressure = 0; pressure <= 5; pressure++) {
            var source = new Endpoint(Fluids.WATER, pressure, 4000);
            var target = new Endpoint(Fluids.WATER, pressure, 0);
            var wrongPressure = new Endpoint(Fluids.WATER, (pressure + 1) % 6, 0);
            var lava = new Endpoint(Fluids.LAVA, pressure, 0);
            var net = new FluidNet(Fluids.WATER);
            try {
                net.addProvider(source);
                net.addReceiver(target);
                net.addReceiver(wrongPressure);
                net.addReceiver(lava);
                net.update();
                h.assertTrue(source.tank.getFill() + target.tank.getFill() == 4000,
                        "Fluid balance changed at pressure " + pressure);
                h.assertTrue(target.tank.getFill() > 0, "Matching pressure failed: " + pressure);
                h.assertTrue(wrongPressure.tank.getFill() == 0 && lava.tank.getFill() == 0,
                        "Mixed pressure/substance at pressure " + pressure);
                var saved = new CompoundTag();
                target.tank.writeToNBT(saved, "tank");
                var restored = new FluidTank(1);
                restored.readFromNBT(saved, "tank");
                h.assertTrue(restored.getPressure() == pressure && restored.getFill() == target.tank.getFill()
                        && restored.getTankType() == Fluids.WATER, "NBT changed pressure/type/amount");
                var handler = restored.getCapability().orElseThrow(IllegalStateException::new);
                int before = restored.getFill();
                int accepted = handler.fill(new FluidStack(Fluids.WATER, 1000), FluidAction.SIMULATE);
                h.assertTrue(accepted == (pressure == 0 ? 1000 : 0),
                        "Forge container ignored the ambient-pressure gate");
                if (pressure > 0) h.assertTrue(handler.fill(new FluidStack(Fluids.WATER, 1000),
                        FluidAction.EXECUTE) == 0, "Forge container filled a pressurized tank");
                handler.drain(1000, FluidAction.SIMULATE);
                h.assertTrue(restored.getFill() == before, "Simulation changed fluid amount");
                var bounded = new Endpoint(Fluids.WATER, pressure, 0);
                h.assertTrue(bounded.tank.fillInternal(Fluids.WATER, 11_000) == 10_000,
                        "Internal fill did not respect capacity");
                h.assertTrue(bounded.tank.fillInternal(Fluids.WATER, 1) == 0
                        && bounded.tank.fillInternal(Fluids.LAVA, 1) == 0
                        && bounded.tank.getFill() == 10_000, "Internal fill mixed or overfilled fluid");
            } finally { net.destroy(); }
        }
        for (int pressure : new int[]{-1, 6}) {
            var invalid = new Endpoint(Fluids.WATER, pressure, 0);
            h.assertTrue(invalid.tank.fillInternal(Fluids.WATER, 1000) == 0
                    && invalid.tank.getFill() == 0, "Internal fill accepted unsupported pressure");
        }
        h.succeed();
    }
}
