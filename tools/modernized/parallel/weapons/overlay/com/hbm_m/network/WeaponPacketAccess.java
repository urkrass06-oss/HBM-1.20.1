/* SPDX-License-Identifier: LGPL-3.0-only */
package com.hbm_m.network;

import io.netty.handler.codec.DecoderException;
import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.entity.BlockEntity;

/** W-01 server-side guards. No target lookup may load a client-selected chunk. */
final class WeaponPacketAccess {
    private WeaponPacketAccess() {}

    static void requireSize(FriendlyByteBuf buffer, int... sizes) {
        for (int size : sizes) if (buffer.readableBytes() == size) return;
        throw new DecoderException("Invalid weapon packet size");
    }

    static boolean active(ServerPlayer player) {
        return player != null && player.getServer().isSameThread()
                && player.isAlive() && !player.isSpectator();
    }

    static boolean loaded(ServerPlayer player, BlockPos pos) {
        return pos != null && player.serverLevel().isInWorldBounds(pos)
                && player.serverLevel().getWorldBorder().isWithinBounds(pos)
                && player.serverLevel().hasChunkAt(pos);
    }

    static boolean nearby(ServerPlayer player, BlockPos pos) {
        return player.distanceToSqr(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5) <= 64;
    }

    static boolean menuTarget(ServerPlayer player, BlockPos pos, BlockEntity target) {
        return active(player) && target != null && target.getLevel() == player.serverLevel()
                && !target.isRemoved() && target.getBlockPos().equals(pos) && loaded(player, pos)
                && player.serverLevel().getBlockEntity(pos) == target
                && player.serverLevel().mayInteract(player, pos)
                && player.containerMenu.stillValid(player);
    }
}
