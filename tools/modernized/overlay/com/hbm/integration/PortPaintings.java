/* SPDX-License-Identifier: LGPL-3.0-only */
package com.hbm.integration;

import com.hbm.HbmPort;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.decoration.PaintingVariant;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;

/** Forge 1.20.1 bridge for Modernized's data-only painting, added 2026-10-19. */
public final class PortPaintings {
    private static final DeferredRegister<PaintingVariant> VARIANTS =
            DeferredRegister.create(Registries.PAINTING_VARIANT, HbmPort.MOD_ID);

    static {
        // Preserve the existing variant ID and 64x48 pixel dimensions; no asset replacement.
        VARIANTS.register("bober1", () -> new PaintingVariant(64, 48));
    }

    private PortPaintings() {
    }

    public static void register(IEventBus modBus) {
        VARIANTS.register(modBus);
    }
}
