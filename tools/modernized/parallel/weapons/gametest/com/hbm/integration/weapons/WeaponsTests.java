/* SPDX-License-Identifier: LGPL-3.0-only */
package com.hbm.integration.weapons;

import com.hbm_m.block.ModBlocks;
import com.hbm_m.blockentity.machines.*;
import com.hbm_m.entity.grenades.GrenadeProjectileEntity;
import com.hbm_m.inventory.menu.*;
import com.hbm_m.item.ModItems;
import com.hbm_m.network.*;
import com.mojang.authlib.GameProfile;
import dev.architectury.networking.NetworkManager.PacketContext;
import io.netty.buffer.Unpooled;
import io.netty.handler.codec.DecoderException;
import java.lang.reflect.Proxy;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.util.FakePlayerFactory;
import net.minecraftforge.event.level.ExplosionEvent;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

/** Exercises the actual handlers on the server thread, including positive controls. */
@GameTestHolder("hbm_m")
@PrefixGameTestTemplate(false)
public final class WeaponsTests {
    private static ServerPlayer player(GameTestHelper h, String name) {
        var p = FakePlayerFactory.get(h.getLevel(), new GameProfile(UUID.nameUUIDFromBytes(
                name.getBytes(java.nio.charset.StandardCharsets.UTF_8)), name));
        p.containerMenu = p.inventoryMenu;
        p.setHealth(p.getMaxHealth());
        p.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
        near(p, h.absolutePos(new BlockPos(2, 2, 2)));
        return p;
    }

    private static void near(ServerPlayer p, BlockPos pos) {
        p.setPos(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5);
    }

    private static PacketContext context(ServerPlayer p) {
        return (PacketContext) Proxy.newProxyInstance(PacketContext.class.getClassLoader(),
                new Class<?>[]{PacketContext.class}, (proxy, method, args) -> {
                    if (method.getName().equals("getPlayer")) return p;
                    if (method.getName().equals("queue")) { ((Runnable) args[0]).run(); return null; }
                    throw new UnsupportedOperationException(method.getName());
                });
    }

    @GameTest(template = "empty")
    public static void weaponPacketsRejectInvalidTargets(GameTestHelper h) {
        BlockPos pos = h.absolutePos(new BlockPos(2, 2, 2));
        h.setBlock(new BlockPos(2, 2, 2), ModBlocks.TURRET_JEREMY.get());
        var turret = (TurretBaseBlockEntity) h.getLevel().getBlockEntity(pos);
        var p = player(h, "WAuthTurret");
        var packet = new TurretControlPacket(pos, TurretControlPacket.ACTION_TOGGLE_ON);
        var before = turret.saveWithFullMetadata();
        try {
            TurretControlPacket.handle(packet, context(p));
            h.assertTrue(before.equals(turret.saveWithFullMetadata()), "Turret changed without its menu");
            p.containerMenu = new TurretMenu(1, p.getInventory(), turret);
            TurretControlPacket.handle(packet, context(p));
            h.assertTrue(!before.equals(turret.saveWithFullMetadata()), "Valid turret control did nothing");
            var changed = turret.saveWithFullMetadata();
            p.setPos(p.getX() + 100, p.getY(), p.getZ());
            TurretControlPacket.handle(packet, context(p));
            h.assertTrue(changed.equals(turret.saveWithFullMetadata()), "Remote turret control accepted");
            near(p, pos);
            p.setGameMode(net.minecraft.world.level.GameType.SPECTATOR);
            TurretControlPacket.handle(packet, context(p));
            h.assertTrue(changed.equals(turret.saveWithFullMetadata()), "Spectator turret control accepted");
            p.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
            TurretControlPacket.handle(new TurretControlPacket(pos, Integer.MAX_VALUE), context(p));
            h.assertTrue(changed.equals(turret.saveWithFullMetadata()), "Invalid turret action changed state");
            // A stale menu must not control a replacement entity at identical coordinates.
            h.setBlock(new BlockPos(2, 2, 2), Blocks.AIR);
            h.setBlock(new BlockPos(2, 2, 2), ModBlocks.TURRET_JEREMY.get());
            var replacement = h.getLevel().getBlockEntity(pos);
            var fresh = replacement.saveWithFullMetadata();
            TurretControlPacket.handle(packet, context(p));
            h.assertTrue(fresh.equals(replacement.saveWithFullMetadata()), "Stale turret menu controlled replacement");
            // The identical position in a different level must never authorize this menu.
            var other = p.getServer().getLevel(net.minecraft.world.level.Level.NETHER);
            h.assertTrue(other != null, "Missing second dimension fixture");
            var foreign = FakePlayerFactory.get(other, new GameProfile(UUID.randomUUID(), "WOtherLevel"));
            near(foreign, pos);
            foreign.containerMenu = new TurretMenu(2, foreign.getInventory(), replacement);
            try {
                TurretControlPacket.handle(packet, context(foreign));
                h.assertTrue(fresh.equals(replacement.saveWithFullMetadata()), "Cross-level turret access changed state");
            } finally { foreign.containerMenu = foreign.inventoryMenu; }
        } finally { p.containerMenu = p.inventoryMenu; }
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void missileAssemblyRequiresItsMatchingMenu(GameTestHelper h) {
        BlockPos rel = new BlockPos(1, 2, 1), pos = h.absolutePos(rel);
        h.setBlock(rel, ModBlocks.MACHINE_MISSILE_ASSEMBLY.get());
        var assembly = (MissileAssemblyBlockEntity) h.getLevel().getBlockEntity(pos);
        var inv = assembly.getInventory();
        inv.setStackInSlot(0, new ItemStack(ModItems.MISSILE_CHIP.get(), 2));
        inv.setStackInSlot(1, new ItemStack(ModItems.WARHEAD_GENERIC_SMALL.get(), 2));
        inv.setStackInSlot(2, new ItemStack(ModItems.MISSILE_FUSELAGE.get(), 2));
        inv.setStackInSlot(4, new ItemStack(ModItems.THRUSTER_SMALL.get(), 2));
        h.assertTrue(assembly.canBuild(), "Invalid assembly fixture");
        var p = player(h, "WAuthMissile");
        near(p, pos);
        var packet = new BuildMissilePacket(pos);
        try {
            var before = assembly.saveWithFullMetadata();
            BuildMissilePacket.handle(packet, context(p));
            h.assertTrue(before.equals(assembly.saveWithFullMetadata()), "Missile built without menu");
            p.containerMenu = new MissileAssemblyMenu(1, p.getInventory(), assembly);
            BuildMissilePacket.handle(packet, context(p));
            h.assertTrue(inv.getStackInSlot(5).getCount() == 1 && inv.getStackInSlot(0).getCount() == 1,
                    "Authorized assembly did not consume exactly one payload");
            BuildMissilePacket.handle(packet, context(p));
            h.assertTrue(inv.getStackInSlot(5).getCount() == 1 && inv.getStackInSlot(0).getCount() == 1,
                    "Repeated assembly duplicated payload");
        } finally { p.containerMenu = p.inventoryMenu; }
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void soyuzRequiresItsMatchingMenu(GameTestHelper h) {
        var p = player(h, "WAuthSoyuz");
        try {
            BlockPos soyRel = new BlockPos(3, 2, 3), soyPos = h.absolutePos(soyRel);
            h.setBlock(soyRel, ModBlocks.SOYUZ_LAUNCHER.get());
            var soyuz = (SoyuzLauncherBlockEntity) h.getLevel().getBlockEntity(soyPos);
            var initial = soyuz.saveWithFullMetadata();
            SoyuzLauncherControlPacket.handle(SoyuzLauncherControlPacket.setMode(soyPos, 1), context(p));
            h.assertTrue(initial.equals(soyuz.saveWithFullMetadata()), "Soyuz accepted wrong menu");
            near(p, soyPos);
            p.containerMenu = new SoyuzLauncherMenu(2, p.getInventory(), soyuz, new SimpleContainerData(5));
            SoyuzLauncherControlPacket.handle(SoyuzLauncherControlPacket.setMode(soyPos, 1), context(p));
            h.assertTrue(!initial.equals(soyuz.saveWithFullMetadata()), "Valid Soyuz mode change rejected");
            var changed = soyuz.saveWithFullMetadata();
            SoyuzLauncherControlPacket.handle(SoyuzLauncherControlPacket.setMode(soyPos, Integer.MAX_VALUE), context(p));
            h.assertTrue(changed.equals(soyuz.saveWithFullMetadata()), "Oversized Soyuz mode changed state");
            p.setPos(p.getX() + 100, p.getY(), p.getZ());
            SoyuzLauncherControlPacket.handle(SoyuzLauncherControlPacket.setMode(soyPos, 0), context(p));
            h.assertTrue(changed.equals(soyuz.saveWithFullMetadata()), "Remote Soyuz control accepted");
        } finally { p.containerMenu = p.inventoryMenu; }
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void radarRejectsWrongMenuAndKeepsLinkedScreenAccess(GameTestHelper h) {
        BlockPos rel = new BlockPos(2, 2, 2), pos = h.absolutePos(rel);
        h.setBlock(rel, ModBlocks.RADAR.get());
        var radar = (MachineRadarBlockEntity) h.getLevel().getBlockEntity(pos);
        var p = player(h, "WAuthRadar");
        var toggle = new UpdateRadarC2SPacket(pos, 0);
        try {
            boolean before = radar.scanMissiles;
            UpdateRadarC2SPacket.handle(toggle, context(p));
            h.assertTrue(radar.scanMissiles == before, "Radar changed without menu");
            p.containerMenu = new MachineRadarMenu(1, p.getInventory(), radar);
            UpdateRadarC2SPacket.handle(toggle, context(p));
            h.assertTrue(radar.scanMissiles != before, "Valid radar toggle rejected");
            p.setPos(p.getX() + 100, p.getY(), p.getZ());
            UpdateRadarC2SPacket.handle(toggle, context(p));
            h.assertTrue(radar.scanMissiles != before, "Unlinked remote radar control accepted");
            // The server's screen link, not the packet, grants remote access.
            BlockPos screenPos = h.absolutePos(new BlockPos(4, 2, 2));
            h.setBlock(new BlockPos(4, 2, 2), ModBlocks.RADAR_SCREEN.get());
            var screen = (MachineRadarScreenBlockEntity) h.getLevel().getBlockEntity(screenPos);
            ItemStack linker = new ItemStack(ModItems.RADAR_LINKER.get());
            var tag = linker.getOrCreateTag();
            tag.putInt("xCoord", screenPos.getX()); tag.putInt("yCoord", screenPos.getY());
            tag.putInt("zCoord", screenPos.getZ());
            radar.getInventory().setStackInSlot(MachineRadarBlockEntity.SLOT_SCREEN_LINKER, linker);
            screen.linked = true;
            screen.refX = pos.getX(); screen.refY = pos.getY(); screen.refZ = pos.getZ();
            // A distant screen within this isolated test's already-loaded chunk.
            BlockPos remote = pos.offset(0, 12, 0);
            var remoteScreen = new MachineRadarScreenBlockEntity(remote, screen.getBlockState());
            h.getLevel().setBlock(remote, screen.getBlockState(), 3);
            h.getLevel().setBlockEntity(remoteScreen);
            tag.putInt("xCoord", remote.getX()); tag.putInt("yCoord", remote.getY()); tag.putInt("zCoord", remote.getZ());
            remoteScreen.linked = true;
            remoteScreen.refX = pos.getX(); remoteScreen.refY = pos.getY(); remoteScreen.refZ = pos.getZ();
            near(p, remote);
            try {
                UpdateRadarC2SPacket.handle(toggle, context(p));
                h.assertTrue(radar.scanMissiles == before, "Linked radar screen access rejected");
                remoteScreen.linked = false;
                UpdateRadarC2SPacket.handle(toggle, context(p));
                h.assertTrue(radar.scanMissiles == before, "Unlinked screen still authorized control");
            } finally { h.getLevel().removeBlock(remote, false); }
        } finally { p.containerMenu = p.inventoryMenu; }
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void detonatorUsesHeldServerItemAndDimension(GameTestHelper h) {
        BlockPos rel = new BlockPos(2, 3, 2), pos = h.absolutePos(rel);
        h.setBlock(rel, ModBlocks.DET_MINER.get());
        var p = player(h, "WDetonator");
        p.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
        var held = new ItemStack(ModItems.MULTI_DETONATOR.get());
        var point = new CompoundTag();
        point.putInt("X", pos.getX()); point.putInt("Y", pos.getY()); point.putInt("Z", pos.getZ());
        point.putString("Name", "WTest"); point.putBoolean("HasTarget", true);
        point.putString("Dimension", h.getLevel().dimension().location().toString());
        var points = new net.minecraft.nbt.ListTag(); points.add(point);
        held.getOrCreateTag().put("Points", points);
        try {
            DetonateAllPacket.handle(new DetonateAllPacket(held.getTag()), context(p));
            h.assertTrue(h.getLevel().getBlockState(pos).is(ModBlocks.DET_MINER.get()),
                    "Packet NBT granted detonation without held detonator");
            p.setItemSlot(EquipmentSlot.OFFHAND, held);
            point.putString("Dimension", "minecraft:the_nether");
            DetonateAllPacket.handle(new DetonateAllPacket(), context(p));
            h.assertTrue(h.getLevel().getBlockState(pos).is(ModBlocks.DET_MINER.get()),
                    "Detonator activated same coordinates in wrong dimension");
            point.putString("Dimension", h.getLevel().dimension().location().toString());
            p.setGameMode(net.minecraft.world.level.GameType.SPECTATOR);
            DetonateAllPacket.handle(new DetonateAllPacket(), context(p));
            h.assertTrue(h.getLevel().getBlockState(pos).is(ModBlocks.DET_MINER.get()),
                    "Spectator detonated a charge");
            p.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
            // Free-use weapon: no container menu or proximity to the charge required.
            p.setPos(p.getX() + 30, p.getY(), p.getZ());
            DetonateAllPacket.handle(new DetonateAllPacket(), context(p));
            h.assertTrue(h.getLevel().getBlockState(pos).isAir(), "Held offhand detonator action rejected");
            DetonateAllPacket.handle(new DetonateAllPacket(), context(p));
            h.assertTrue(h.getLevel().getBlockState(pos).isAir(), "Repeated detonation recreated charge");
        } finally {
            p.setItemSlot(EquipmentSlot.OFFHAND, ItemStack.EMPTY);
            p.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
        }
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void radarValidatesLoadedReceiverAndDetectedEntity(GameTestHelper h) {
        BlockPos radarRel = new BlockPos(1, 2, 1), launchRel = new BlockPos(3, 2, 3);
        h.setBlock(radarRel, ModBlocks.RADAR.get());
        h.setBlock(launchRel, ModBlocks.LAUNCH_PAD.get());
        var radar = (MachineRadarBlockEntity) h.getLevel().getBlockEntity(h.absolutePos(radarRel));
        class Receiver extends LaunchPadBlockEntity {
            int calls;
            Receiver() { super(h.absolutePos(launchRel), h.getBlockState(launchRel)); }
            @Override public boolean sendCommandPosition(BlockPos target) { calls++; return true; }
            @Override public boolean sendCommandEntity(net.minecraft.world.entity.Entity target) { calls++; return true; }
        }
        var receiver = new Receiver();
        h.getLevel().setBlockEntity(receiver);
        ItemStack linker = new ItemStack(ModItems.RADAR_LINKER.get());
        var tag = linker.getOrCreateTag();
        BlockPos launchPos = receiver.getBlockPos();
        tag.putInt("xCoord", launchPos.getX()); tag.putInt("yCoord", launchPos.getY()); tag.putInt("zCoord", launchPos.getZ());
        radar.getInventory().setStackInSlot(0, linker);
        var pig = net.minecraft.world.entity.EntityType.PIG.create(h.getLevel());
        pig.setPos(Vec3.atCenterOf(h.absolutePos(new BlockPos(2, 3, 2))));
        h.getLevel().addFreshEntity(pig);
        try {
            h.assertTrue(!radar.handleLaunchCommand(0, 10, pig.getId(), 0, 0) && receiver.calls == 0,
                    "Radar launched at an undetected entity");
            radar.nearbyMissiles.add(new int[]{0, 0, 0, 0, 0, 0, pig.getId()});
            h.assertTrue(radar.handleLaunchCommand(0, 10, pig.getId(), 0, 0) && receiver.calls == 1,
                    "Detected in-range entity rejected");
            h.assertTrue(radar.handleLaunchCommand(0, 11, -1, launchPos.getX(), launchPos.getZ()) && receiver.calls == 2,
                    "Valid coordinate command rejected");
            h.assertTrue(!radar.handleLaunchCommand(0, 11, -1, Integer.MAX_VALUE, 0) && receiver.calls == 2,
                    "Out-of-world coordinate reached launcher");
            BlockPos unloaded = new BlockPos(20_000_000, launchPos.getY(), 20_000_000);
            h.assertTrue(!h.getLevel().hasChunkAt(unloaded), "Unloaded target fixture was loaded");
            tag.putInt("xCoord", unloaded.getX()); tag.putInt("zCoord", unloaded.getZ());
            h.assertTrue(!radar.handleLaunchCommand(0, 11, -1, launchPos.getX(), launchPos.getZ()),
                    "Unloaded receiver accepted");
            h.assertTrue(!h.getLevel().hasChunkAt(unloaded), "Radar command loaded attacker-selected receiver chunk");
        } finally { pig.discard(); h.setBlock(launchRel, Blocks.AIR); }
        h.succeed();
    }

    private static void rejected(java.util.List<String> accepted, Consumer<FriendlyByteBuf> write,
                                 Consumer<FriendlyByteBuf> decode, String name) {
        var b = new FriendlyByteBuf(Unpooled.buffer());
        try {
            write.accept(b);
            boolean rejected = false;
            try { decode.accept(b); }
            catch (DecoderException | IndexOutOfBoundsException expected) { rejected = true; }
            if (!rejected) accepted.add(name);
        } finally { b.release(); }
    }

    private static void roundTrip(GameTestHelper h, Consumer<FriendlyByteBuf> write,
                                  Consumer<FriendlyByteBuf> decode) {
        var b = new FriendlyByteBuf(Unpooled.buffer());
        try {
            write.accept(b);
            decode.accept(b);
            h.assertTrue(!b.isReadable(), "Valid packet left unread wire data");
        } finally { b.release(); }
    }

    @GameTest(template = "empty")
    public static void weaponDecodersBoundPayloads(GameTestHelper h) {
        var accepted = new java.util.ArrayList<String>();
        rejected(accepted, b -> new TurretControlPacket(BlockPos.ZERO, 6).write(b), TurretControlPacket::decode, "turret action");
        rejected(accepted, b -> SoyuzLauncherControlPacket.setMode(BlockPos.ZERO, Integer.MAX_VALUE).write(b),
                SoyuzLauncherControlPacket::decode, "Soyuz mode");
        rejected(accepted, b -> UpdateRadarC2SPacket.launchAtCoords(BlockPos.ZERO, 8, 0, 0).write(b),
                UpdateRadarC2SPacket::decode, "radar slot");
        rejected(accepted, b -> UpdateRadarC2SPacket.launchAtCoords(BlockPos.ZERO, 0, Integer.MAX_VALUE, 0).write(b),
                UpdateRadarC2SPacket::decode, "radar coordinate");
        for (double value : new double[]{Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY}) {
            CompoundTag tag = new CompoundTag(); tag.putDouble("value", value);
            rejected(accepted, b -> b.writeNbt(tag), DetonateAllPacket::decode, "nonempty/nonfinite detonator NBT");
        }
        rejected(accepted, b -> { new BuildMissilePacket(BlockPos.ZERO).write(b); b.writeZero(1024); },
                BuildMissilePacket::decode, "oversized fixed packet");
        rejected(accepted, b -> { b.writeByte(10); b.writeZero(4096); }, DetonateAllPacket::decode, "oversized NBT");
        h.assertTrue(accepted.isEmpty(), "Malformed weapon payloads accepted: " + accepted);
        roundTrip(h, b -> new BuildMissilePacket(BlockPos.ZERO).write(b), BuildMissilePacket::decode);
        roundTrip(h, b -> new TurretControlPacket(BlockPos.ZERO, 5).write(b), TurretControlPacket::decode);
        roundTrip(h, b -> SoyuzLauncherControlPacket.setMode(BlockPos.ZERO, 1).write(b), SoyuzLauncherControlPacket::decode);
        roundTrip(h, b -> SoyuzLauncherControlPacket.start(BlockPos.ZERO).write(b), SoyuzLauncherControlPacket::decode);
        roundTrip(h, b -> new UpdateRadarC2SPacket(BlockPos.ZERO, 0).write(b), UpdateRadarC2SPacket::decode);
        roundTrip(h, b -> UpdateRadarC2SPacket.openSlots(BlockPos.ZERO).write(b), UpdateRadarC2SPacket::decode);
        roundTrip(h, b -> UpdateRadarC2SPacket.openMain(BlockPos.ZERO).write(b), UpdateRadarC2SPacket::decode);
        roundTrip(h, b -> UpdateRadarC2SPacket.launchAtEntity(BlockPos.ZERO, 7, 0).write(b), UpdateRadarC2SPacket::decode);
        roundTrip(h, b -> UpdateRadarC2SPacket.launchAtCoords(BlockPos.ZERO, 0, 1, -1).write(b), UpdateRadarC2SPacket::decode);
        roundTrip(h, b -> new DetonateAllPacket().write(b), DetonateAllPacket::decode);
        roundTrip(h, b -> b.writeNbt(null), DetonateAllPacket::decode);
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void grenadeHasOwnerAndOneDetonation(GameTestHelper h) {
        var p = player(h, "WGrenadeOwner");
        p.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(ModItems.GRENADE.get(), 2));
        var bounds = new net.minecraft.world.phys.AABB(h.absolutePos(BlockPos.ZERO)).inflate(8);
        var existing = h.getLevel().getEntitiesOfClass(GrenadeProjectileEntity.class, bounds);
        ModItems.GRENADE.get().use(h.getLevel(), p, InteractionHand.MAIN_HAND);
        var spawned = h.getLevel().getEntitiesOfClass(GrenadeProjectileEntity.class, bounds);
        spawned.removeAll(existing);
        h.assertTrue(spawned.size() == 1 && p.getMainHandItem().getCount() == 1,
                "Item use must consume one item and spawn one grenade");
        var grenade = spawned.get(0);
        h.assertTrue(grenade.getOwner() == p, "Grenade lost player owner");
        grenade.setNoGravity(true);
        grenade.setDeltaMovement(Vec3.ZERO);
        grenade.setPos(Vec3.atCenterOf(h.absolutePos(new BlockPos(2, 3, 2))));
        AtomicInteger count = new AtomicInteger();
        Consumer<ExplosionEvent.Start> listener = event -> {
            if (event.getExplosion().getDirectSourceEntity() == grenade) {
                count.incrementAndGet();
                h.assertTrue(event.getExplosion().getIndirectSourceEntity() == p, "Explosion lost grenade owner");
                // Re-entry while explosion callbacks execute must not detonate twice.
                grenade.tick();
                event.setCanceled(true); // Keep neighboring GameTest structures intact.
            }
        };
        MinecraftForge.EVENT_BUS.addListener(net.minecraftforge.eventbus.api.EventPriority.NORMAL,
                false, ExplosionEvent.Start.class, listener);
        try {
            // O ItemGrenadeFuze.FUZE_3S detonates at 60 ticks (selected S3 configuration).
            // Explicit provisional mapping for M STANDARD; no measured O parity claim.
            for (int i = 0; i < 59; i++) grenade.tick();
            h.assertTrue(!grenade.isRemoved() && count.get() == 0, "Grenade detonated before 60 ticks");
            grenade.tick();
            h.assertTrue(grenade.isRemoved() && count.get() == 1, "Grenade did not detonate once at 60 ticks");
            grenade.tick();
            h.assertTrue(count.get() == 1, "Removed grenade detonated again");
        } finally {
            MinecraftForge.EVENT_BUS.unregister(listener);
            grenade.discard();
            p.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
        }
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void grenadeCollisionCannotDetonateTwiceReentrantly(GameTestHelper h) throws Exception {
        var p = player(h, "WGrenadeImpact");
        p.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(ModItems.GRENADESMART.get()));
        var bounds = new net.minecraft.world.phys.AABB(h.absolutePos(BlockPos.ZERO)).inflate(8);
        var existing = h.getLevel().getEntitiesOfClass(GrenadeProjectileEntity.class, bounds);
        ModItems.GRENADESMART.get().use(h.getLevel(), p, InteractionHand.MAIN_HAND);
        var spawned = h.getLevel().getEntitiesOfClass(GrenadeProjectileEntity.class, bounds);
        spawned.removeAll(existing);
        h.assertTrue(spawned.size() == 1, "Smart grenade item did not spawn exactly once");
        var grenade = spawned.get(0);
        var collision = GrenadeProjectileEntity.class.getDeclaredMethod("onHitEntity",
                net.minecraft.world.phys.EntityHitResult.class);
        collision.setAccessible(true);
        Runnable hit = () -> {
            try { collision.invoke(grenade, new net.minecraft.world.phys.EntityHitResult(p)); }
            catch (ReflectiveOperationException e) { throw new RuntimeException(e); }
        };
        AtomicInteger count = new AtomicInteger();
        var damageOwner = new java.util.concurrent.atomic.AtomicReference<net.minecraft.world.entity.Entity>();
        var victim = net.minecraft.world.entity.EntityType.PIG.create(h.getLevel());
        victim.setPos(p.position());
        h.getLevel().addFreshEntity(victim);
        Consumer<net.minecraftforge.event.entity.living.LivingHurtEvent> hurt = event -> {
            if (event.getEntity() == victim && event.getSource().getDirectEntity() == grenade)
                damageOwner.set(event.getSource().getEntity());
        };
        Consumer<ExplosionEvent.Start> listener = event -> {
            if (event.getExplosion().getDirectSourceEntity() == grenade) {
                int n = count.incrementAndGet();
                if (n == 1) hit.run();
                event.setCanceled(true);
            }
        };
        MinecraftForge.EVENT_BUS.addListener(net.minecraftforge.eventbus.api.EventPriority.NORMAL,
                false, ExplosionEvent.Start.class, listener);
        MinecraftForge.EVENT_BUS.addListener(net.minecraftforge.eventbus.api.EventPriority.NORMAL,
                false, net.minecraftforge.event.entity.living.LivingHurtEvent.class, hurt);
        try {
            hit.run(); hit.run();
            h.assertTrue(damageOwner.get() == p, "Custom grenade damage lost the player owner; explosion count=" + count.get());
            h.assertTrue(count.get() == 1 && grenade.isRemoved(), "Re-entrant collision detonated grenade twice");
        } finally {
            MinecraftForge.EVENT_BUS.unregister(listener);
            MinecraftForge.EVENT_BUS.unregister(hurt);
            grenade.discard();
            victim.discard();
            p.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
        }
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void grenadeFuseAndOwnerSurviveNbtRoundTrip(GameTestHelper h) {
        var p = player(h, "WFuseSave");
        var grenade = new GrenadeProjectileEntity(com.hbm_m.entity.ModEntities.GRENADE_PROJECTILE.get(),
                h.getLevel(), p, com.hbm_m.entity.grenades.GrenadeType.STANDARD);
        grenade.setNoGravity(true); grenade.setDeltaMovement(Vec3.ZERO);
        grenade.setPos(Vec3.atCenterOf(h.absolutePos(new BlockPos(2, 3, 2))));
        for (int i = 0; i < 30; i++) grenade.tick();
        CompoundTag saved = new CompoundTag(); grenade.saveWithoutId(saved);
        h.assertTrue(saved.hasUUID("Owner") && saved.getUUID("Owner").equals(p.getUUID()), "Owner UUID not persisted");
        var restored = new GrenadeProjectileEntity(com.hbm_m.entity.ModEntities.GRENADE_PROJECTILE.get(), h.getLevel());
        restored.load(saved);
        AtomicInteger count = new AtomicInteger();
        Consumer<ExplosionEvent.Start> listener = event -> {
            if (event.getExplosion().getDirectSourceEntity() == restored) {
                count.incrementAndGet(); event.setCanceled(true);
            }
        };
        MinecraftForge.EVENT_BUS.addListener(net.minecraftforge.eventbus.api.EventPriority.NORMAL,
                false, ExplosionEvent.Start.class, listener);
        try {
            for (int i = 0; i < 29; i++) restored.tick();
            h.assertTrue(count.get() == 0 && !restored.isRemoved(), "Reload shortened grenade fuse");
            restored.tick();
            h.assertTrue(count.get() == 1 && restored.isRemoved(), "Reload reset or lost grenade fuse");
        } finally {
            MinecraftForge.EVENT_BUS.unregister(listener);
            grenade.discard(); restored.discard();
        }
        h.succeed();
    }
}
