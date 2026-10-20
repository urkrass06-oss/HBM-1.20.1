/* SPDX-License-Identifier: LGPL-3.0-only */
package com.hbm.integration.rendering;

import com.google.gson.JsonParser;
import com.hbm.HbmPort;
import com.hbm_m.main.ForgeEntrypoint;
import java.io.InputStreamReader;
import java.io.File;
import java.nio.charset.StandardCharsets;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.gametest.framework.GlobalTestReporter;
import net.minecraft.gametest.framework.JUnitLikeTestReporter;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

/** Integration wiring checks, independently written; no rendering/parity claim. */
@GameTestHolder("hbm_m")
@PrefixGameTestTemplate(false)
public final class RenderingIntegrationTests {
    static {
        // Loaded by Forge's test discovery before any test executes. The report
        // covers the entire suite, including the unchanged fourteen regressions.
        try {
            GlobalTestReporter.replaceWith(new JUnitLikeTestReporter(new File("hbm-gametest-results.xml")));
        } catch (Exception error) {
            throw new ExceptionInInitializerError(error);
        }
    }

    @GameTest(template = "empty", required = true)
    public static void singleOwningModContainer(GameTestHelper helper) {
        long containers = ModList.get().getMods().stream()
                .filter(info -> info.getModId().equals("hbm_m")).count();
        helper.assertTrue(containers == 1, "Expected exactly one owning hbm_m mod container");
        helper.assertTrue(HbmPort.class.getAnnotation(Mod.class).value().equals("hbm_m"),
                "Foundation entrypoint lost the Modernized namespace");
        helper.assertTrue(ForgeEntrypoint.class.getAnnotation(Mod.class) == null,
                "Upstream delegate became a second entrypoint");
        helper.succeed();
    }

    @GameTest(template = "empty", required = true)
    public static void declaredRegistryDeltaExists(GameTestHelper helper) throws Exception {
        var stream = RenderingIntegrationTests.class.getResourceAsStream("/hbm-parallel-contract.json");
        helper.assertTrue(stream != null, "Loader did not generate the test-only registry contract");
        try (var reader = new InputStreamReader(stream, StandardCharsets.UTF_8)) {
            var contract = JsonParser.parseReader(reader).getAsJsonObject();
            for (var element : contract.getAsJsonArray("registrations")) {
                var row = element.getAsJsonObject();
                var registryId = new ResourceLocation("minecraft", row.get("registry").getAsString());
                Registry<?> registry = (Registry<?>) BuiltInRegistries.REGISTRY.get(registryId);
                helper.assertTrue(registry != null, "Unknown registry: " + registryId);
                var id = new ResourceLocation(row.get("id").getAsString());
                helper.assertTrue(registry.containsKey(id), "Declared registration missing: " + registryId + "/" + id);
            }
        }
        helper.succeed();
    }
}
