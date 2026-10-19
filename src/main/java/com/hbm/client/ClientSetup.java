/* SPDX-License-Identifier: LGPL-3.0-only */
package com.hbm.client;

import com.hbm.HbmPort;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

/** Physical-client lifecycle code stays outside the common entry point. */
@Mod.EventBusSubscriber(modid = HbmPort.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class ClientSetup {
    private ClientSetup() {
    }

    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        HbmPort.LOGGER.info("HBM port client foundation initialized.");
    }
}
