/* SPDX-License-Identifier: LGPL-3.0-only */
package com.hbm.integration;

import com.hbm_m.api.energy.EnergyNetworkManager;
import com.hbm_m.api.energy.LongEnergyWrapper;
import com.hbm_m.api.fluids.FluidNetProvider;
import com.hbm_m.block.ModBlocks;
import com.hbm_m.blockentity.machines.MachineBatteryBlockEntity;
import com.hbm_m.blockentity.machines.MachineFluidTankBlockEntity;
import com.hbm_m.blockentity.machines.MachineRbmkConsoleBlockEntity;
import com.hbm_m.blockentity.machines.rbmk.RBMKControlBlockEntity;
import com.hbm_m.inventory.fluid.ModFluids;
import com.hbm_m.inventory.fluid.tank.FluidTank;
import com.hbm_m.network.RBMKConsoleControlPacket;
import io.netty.buffer.Unpooled;
import io.netty.handler.codec.DecoderException;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.level.material.Fluids;
import net.minecraftforge.fluids.FluidStack;
import net.minecraftforge.fluids.capability.IFluidHandler.FluidAction;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

/** Concrete server-side contracts, not a substitute for two-client observations. */
@GameTestHolder("hbm_m")
@PrefixGameTestTemplate(false)
public final class ModernizedSystemsTests {
    @GameTest(template = "empty")
    public static void highEnergyUnitMustFitIncludingRemainder(GameTestHelper helper) {
        var battery = new MachineBatteryBlockEntity(BlockPos.ZERO,
                ModBlocks.MACHINE_BATTERY_SCHRABIDIUM.get().defaultBlockState());
        CompoundTag saved = battery.saveWithFullMetadata();
        long unit = 1L << 32;
        saved.putLong("capacity", 2 * unit + 50);
        saved.putLong("energy", unit + 100);
        battery.load(saved);
        var high = new LongEnergyWrapper(battery, LongEnergyWrapper.BitMode.HIGH);
        helper.assertTrue(high.receiveEnergy(1, true) == 0, "Partial HIGH unit reported as a whole unit");
        helper.assertTrue(high.receiveEnergy(1, false) == 0 && battery.getEnergyStored() == unit + 100,
                "HIGH transfer exceeded available capacity");
        saved.putLong("energy", unit);
        battery.load(saved);
        helper.assertTrue(high.receiveEnergy(1, true) == 1 && battery.getEnergyStored() == unit,
                "HIGH simulation failed or mutated storage");
        helper.assertTrue(high.receiveEnergy(1, false) == 1 && battery.getEnergyStored() == 2 * unit,
                "Whole HIGH unit was not preserved");
        helper.succeed();
    }

    @GameTest(template = "empty")
    public static void rbmkRequiresTheMatchingNearbyOpenMenu(GameTestHelper helper) {
        BlockPos relative = new BlockPos(1, 2, 1), otherPos = new BlockPos(3, 2, 1);
        helper.setBlock(relative, ModBlocks.RBMK_CONSOLE.get().defaultBlockState());
        helper.setBlock(otherPos, ModBlocks.RBMK_CONSOLE.get().defaultBlockState());
        var console = (MachineRbmkConsoleBlockEntity) helper.getLevel().getBlockEntity(helper.absolutePos(relative));
        var other = (MachineRbmkConsoleBlockEntity) helper.getLevel().getBlockEntity(helper.absolutePos(otherPos));
        var player = net.minecraftforge.common.util.FakePlayerFactory.get(helper.getLevel(),
                new com.mojang.authlib.GameProfile(java.util.UUID.fromString("edfa43fa-2fb9-4c6a-a469-01fdcb29cb15"), "HBMAuthTest"));
        var menu = new com.hbm_m.inventory.menu.MachineRbmkConsoleMenu(1, player.getInventory(), console);
        var packet = new RBMKConsoleControlPacket(console.getBlockPos(), 3, 0, 0, new int[0]);
        player.setPos(console.getBlockPos().getX() + 0.5, console.getBlockPos().getY(), console.getBlockPos().getZ() + 0.5);
        try {
            player.containerMenu = player.inventoryMenu;
            helper.assertTrue(!packet.apply(player), "Control without an open console menu accepted");
            player.containerMenu = new com.hbm_m.inventory.menu.MachineRbmkConsoleMenu(2, player.getInventory(), other);
            helper.assertTrue(!packet.apply(player), "Control through a different console accepted");
            player.containerMenu = menu;
            helper.assertTrue(packet.apply(player), "Nearby matching menu control rejected");
            player.setPos(player.getX() + 100, player.getY(), player.getZ());
            helper.assertTrue(!packet.apply(player), "Remote control accepted");
            player.setPos(console.getBlockPos().getX() + 0.5, console.getBlockPos().getY(), console.getBlockPos().getZ() + 0.5);
            helper.setBlock(relative, net.minecraft.world.level.block.Blocks.AIR);
            helper.assertTrue(!packet.apply(player), "Stale removed console accepted");
        } finally { player.containerMenu = player.inventoryMenu; }
        helper.succeed();
    }

    @GameTest(template = "empty")
    public static void forgeEnergyBoundsAndSimulation(GameTestHelper helper) {
        var battery = new MachineBatteryBlockEntity(BlockPos.ZERO,
                ModBlocks.MACHINE_BATTERY_SCHRABIDIUM.get().defaultBlockState());
        battery.setEnergyStored(4_294_967_295L);
        var wrapper = new LongEnergyWrapper(battery, LongEnergyWrapper.BitMode.LOW);
        helper.assertTrue(wrapper.getEnergyStored() == Integer.MAX_VALUE, "FE stored value is not saturated");
        helper.assertTrue(wrapper.getMaxEnergyStored() == Integer.MAX_VALUE, "FE capacity is not saturated");
        long before = battery.getEnergyStored();
        helper.assertTrue(wrapper.extractEnergy(1234, true) == 1234, "FE simulated extraction failed");
        helper.assertTrue(wrapper.receiveEnergy(1234, true) == 1234, "FE simulated insertion failed");
        helper.assertTrue(battery.getEnergyStored() == before, "FE simulation changed storage");
        helper.assertTrue(wrapper.extractEnergy(-1, false) == 0, "FE accepted negative extraction");
        helper.assertTrue(wrapper.receiveEnergy(-1, false) == 0, "FE accepted negative insertion");
        helper.assertTrue(battery.getEnergyStored() == before, "Invalid FE argument changed storage");
        helper.succeed();
    }

    private static MachineBatteryBlockEntity battery(GameTestHelper helper, int x) {
        BlockPos relative = new BlockPos(x, 2, 1);
        helper.setBlock(relative, ModBlocks.MACHINE_BATTERY_SCHRABIDIUM.get().defaultBlockState());
        return (MachineBatteryBlockEntity) helper.getLevel().getBlockEntity(helper.absolutePos(relative));
    }

    @GameTest(template = "empty", timeoutTicks = 100)
    public static void wireTransfersEnergyWithoutLoss(GameTestHelper helper) {
        var source = battery(helper, 1);
        helper.setBlock(new BlockPos(2, 2, 1), ModBlocks.WIRE_COATED.get().defaultBlockState());
        var target = battery(helper, 3);
        source.modeOnNoSignal = source.modeOnSignal = 2;
        target.modeOnNoSignal = target.modeOnSignal = 1;
        source.setEnergyStored(20_000_000L);
        target.setEnergyStored(0);
        helper.runAfterDelay(30, () -> {
            helper.assertTrue(target.getEnergyStored() > 0, "No energy passed through the wire");
            helper.assertTrue(source.getEnergyStored() + target.getEnergyStored() == 20_000_000L,
                    "Wire transfer created or lost energy");
            helper.succeed();
        });
    }

    @GameTest(template = "empty")
    public static void energyManagerRunsOncePerLevelTick(GameTestHelper helper) {
        var placedSource = battery(helper, 1);
        var placedTarget = battery(helper, 2);
        var source = new MachineBatteryBlockEntity(placedSource.getBlockPos(), placedSource.getBlockState()) {
            @Override public long getProvideSpeed() { return 1000; }
        };
        var target = new MachineBatteryBlockEntity(placedTarget.getBlockPos(), placedTarget.getBlockState()) {
            @Override public long getReceiveSpeed() { return 1000; }
        };
        helper.getLevel().setBlockEntity(source);
        helper.getLevel().setBlockEntity(target);
        source.modeOnNoSignal = source.modeOnSignal = 2;
        target.modeOnNoSignal = target.modeOnSignal = 1;
        // Real world/capabilities with a controlled per-tick budget: a duplicate
        // network tick would transfer a second 1000 HE and violate this budget.
        var manager = EnergyNetworkManager.get(helper.getLevel());
        source.setEnergyStored(20_000_000L);
        target.setEnergyStored(0);
        manager.addNode(source.getBlockPos());
        manager.addNode(target.getBlockPos());
        manager.tick();
        long first = target.getEnergyStored();
        helper.assertTrue(first <= 1000, "First network call exceeded per-tick budget");
        manager.tick();
        helper.assertTrue(target.getEnergyStored() == first, "Repeated manager invocation changed the same tick");
        helper.succeed();
    }

    @GameTest(template = "empty")
    public static void rbmkIncrementalPacketAppliesColumns(GameTestHelper helper) {
        var state = ModBlocks.RBMK_CONSOLE.get().defaultBlockState();
        var server = new MachineRbmkConsoleBlockEntity(BlockPos.ZERO, state);
        var client = new MachineRbmkConsoleBlockEntity(BlockPos.ZERO, state);
        CompoundTag data = new CompoundTag();
        data.putDouble("level", 0.5);
        server.columns[0] = new MachineRbmkConsoleBlockEntity.RBMKColumnData(
                RBMKControlBlockEntity.ColumnType.CONTROL, data);
        client.onDataPacket(null, net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket.create(server));
        helper.assertTrue(client.columns[0] != null && client.columns[0].data.getDouble("level") == 0.5,
                "RBMK incremental packet lost column data");
        server.columns[0] = null;
        client.onDataPacket(null, net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket.create(server));
        helper.assertTrue(client.columns[0] == null, "RBMK incremental packet retained a removed column");
        helper.succeed();
    }

    @GameTest(template = "empty")
    public static void fluidSimulationEquivalenceAndPersistence(GameTestHelper helper) {
        var tank = new FluidTank(10_000);
        var handler = tank.getCapability().orElseThrow(IllegalStateException::new);
        helper.assertTrue(handler.fill(new FluidStack(Fluids.WATER, 4000), FluidAction.SIMULATE) == 4000,
                "Fluid simulated fill failed");
        helper.assertTrue(tank.getFluidAmountMb() == 0, "Fluid simulation mutated tank");
        helper.assertTrue(tank.fillMb(Fluids.WATER, 4000) == 4000, "Water fill failed");
        helper.assertTrue(tank.fillMb(ModFluids.WATER.getSource(), 1000) == 1000, "HBM/vanilla water not equivalent");
        helper.assertTrue(tank.fillMb(Fluids.LAVA, 1000) == 0, "Water and lava mixed");
        helper.assertTrue(handler.drain(1000, FluidAction.SIMULATE).getAmount() == 1000,
                "Fluid simulated drain failed");
        helper.assertTrue(tank.getFluidAmountMb() == 5000, "Simulated drain mutated tank");
        CompoundTag saved = new CompoundTag();
        tank.writeToNBT(saved, "test");
        var restored = new FluidTank(1);
        restored.readFromNBT(saved, "test");
        helper.assertTrue(restored.getCapacityMb() == 10_000 && restored.getFluidAmountMb() == 5000,
                "Fluid amount/capacity changed on load");
        helper.assertTrue(FluidNetProvider.forFluid(Fluids.WATER) == FluidNetProvider.forFluid(ModFluids.WATER.getSource()),
                "Equivalent fluids use different network identities");
        helper.succeed();
    }

    @GameTest(template = "empty", timeoutTicks = 100)
    public static void tankMultiblockFormsAndPersists(GameTestHelper helper) {
        BlockPos relative = new BlockPos(2, 2, 1);
        helper.setBlock(relative, ModBlocks.FLUID_TANK.get().defaultBlockState());
        var entity = helper.getLevel().getBlockEntity(helper.absolutePos(relative));
        helper.assertTrue(entity instanceof MachineFluidTankBlockEntity, "Tank controller missing");
        var tank = (MachineFluidTankBlockEntity) entity;
        tank.getFluidTank().fillMb(Fluids.WATER, 16_000);
        helper.runAfterDelay(10, () -> {
            int parts = 0;
            for (int x = 0; x < 5; x++) for (int y = 2; y < 5; y++) for (int z = 1; z < 4; z++) {
                if (helper.getBlockState(new BlockPos(x, y, z)).is(ModBlocks.UNIVERSAL_MACHINE_PART.get())) parts++;
            }
            helper.assertTrue(parts == 38, "Tank structure has " + parts + " parts, expected 38");
            var restored = new MachineFluidTankBlockEntity(tank.getBlockPos(), tank.getBlockState());
            restored.load(tank.saveWithFullMetadata());
            helper.assertTrue(restored.getFluidTank().getFluidAmountMb() == 16_000, "Tank lost fluid on load");
            helper.succeed();
        });
    }

    @GameTest(template = "empty", timeoutTicks = 100)
    public static void rbmkControlAndEmergencyShutdown(GameTestHelper helper) {
        BlockPos consolePos = new BlockPos(1, 2, 1), rodPos = new BlockPos(3, 2, 1);
        helper.setBlock(consolePos, ModBlocks.RBMK_CONSOLE.get().defaultBlockState());
        helper.setBlock(rodPos, ModBlocks.RBMK_CONTROL.get().defaultBlockState());
        var console = (MachineRbmkConsoleBlockEntity) helper.getLevel().getBlockEntity(helper.absolutePos(consolePos));
        var rod = (RBMKControlBlockEntity) helper.getLevel().getBlockEntity(helper.absolutePos(rodPos));
        console.reactorOrigin = rod.getBlockPos();
        console.handleControl(helper.getLevel(), 0, 0.25, 0, new int[]{0});
        helper.assertTrue(rod.targetLevel == 0.25, "Console did not set control rod target");
        console.handleControl(helper.getLevel(), 2, 0, 3, new int[]{0});
        helper.assertTrue(rod.color == 3, "Console color assignment failed");
        console.handleControl(helper.getLevel(), 1, 0, 0, new int[0]);
        helper.assertTrue(rod.targetLevel == 0 && rod.level == 0, "AZ-5 did not insert control rod");
        helper.succeed();
    }

    @GameTest(template = "empty")
    public static void rbmkPacketRejectsMalformedPayloads(GameTestHelper helper) {
        // Small local buffers only: never allocate an attacker-specified large array.
        for (int length : new int[]{-1, 226}) {
            var buffer = new FriendlyByteBuf(Unpooled.buffer());
            try {
                buffer.writeBlockPos(BlockPos.ZERO).writeByte(0).writeDouble(0.5).writeInt(0).writeInt(length);
                for (int i = 0; i < Math.max(length, 0); i++) buffer.writeInt(0);
                boolean rejected = false;
                try { RBMKConsoleControlPacket.decode(buffer); }
                catch (DecoderException expected) { rejected = true; }
                helper.assertTrue(rejected, "Invalid RBMK array length accepted: " + length);
            } finally { buffer.release(); }
        }
        var valid = new FriendlyByteBuf(Unpooled.buffer());
        try {
            new RBMKConsoleControlPacket(BlockPos.ZERO, 0, 0.5, 0, new int[]{0, 224}).write(valid);
            RBMKConsoleControlPacket.decode(valid);
        } finally { valid.release(); }
        helper.succeed();
    }

    @GameTest(template = "empty")
    public static void rbmkPacketRejectsInvalidActionsAndNumbers(GameTestHelper helper) {
        var packets = new RBMKConsoleControlPacket[]{
            new RBMKConsoleControlPacket(BlockPos.ZERO, 6, 0, 0, new int[0]),
            new RBMKConsoleControlPacket(BlockPos.ZERO, 0, Double.NaN, 0, new int[]{0}),
            new RBMKConsoleControlPacket(BlockPos.ZERO, 0, 1.1, 0, new int[]{0}),
            new RBMKConsoleControlPacket(BlockPos.ZERO, 0, 0.5, 0, new int[]{225}),
            new RBMKConsoleControlPacket(BlockPos.ZERO, 2, 0, 5, new int[]{0}),
            new RBMKConsoleControlPacket(BlockPos.ZERO, 3, 0, 6, new int[0]),
            new RBMKConsoleControlPacket(BlockPos.ZERO, 4, 0, 0, new int[]{1, 2}),
        };
        for (var packet : packets) {
            var buffer = new FriendlyByteBuf(Unpooled.buffer());
            try {
                packet.write(buffer);
                boolean rejected = false;
                try { RBMKConsoleControlPacket.decode(buffer); }
                catch (DecoderException expected) { rejected = true; }
                helper.assertTrue(rejected, "Invalid RBMK control payload accepted");
            } finally { buffer.release(); }
        }
        helper.succeed();
    }
}
