/* SPDX-License-Identifier: LGPL-3.0-only */
package com.hbm;

import com.hbm.registry.ModRegistries;
import com.mojang.logging.LogUtils;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;

/** Entry point for the Forge 1.20.1 port; no original game content is registered yet. */
@Mod(HbmPort.MOD_ID)
public final class HbmPort {
    public static final String MOD_ID = "hbm";
    public static final Logger LOGGER = LogUtils.getLogger();

    public HbmPort(FMLJavaModLoadingContext context) {
        IEventBus modBus = context.getModEventBus();
        ModRegistries.register(modBus);
        modBus.addListener(this::commonSetup);
    }

    private void commonSetup(FMLCommonSetupEvent event) {
        LOGGER.info("HBM Forge 1.20.1 port foundation initialized; no gameplay content is implemented.");
    }
}
