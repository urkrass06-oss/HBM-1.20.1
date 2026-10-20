/* SPDX-License-Identifier: LGPL-3.0-only */
package com.hbm.integration;

import com.hbm.HbmPort;
import com.hbm_m.block.ModBlocks;
import com.hbm_m.blockentity.machines.MachineBatteryBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import net.minecraftforge.registries.ForgeRegistries;

/** Integration smoke tests; deliberately make no original-HBM parity claim. */
@GameTestHolder("hbm_m")
@PrefixGameTestTemplate(false)
public final class ModernizedIntegrationTests {
    @GameTest(template = "empty", timeoutTicks = 100)
    public static void registriesAndGeneratedRecipes(GameTestHelper helper) {
        helper.assertTrue("hbm_m".equals(HbmPort.MOD_ID), "Mod namespace changed");
        for (String name : new String[]{"machine_battery", "machine_assembler", "press"}) {
            helper.assertTrue(ForgeRegistries.BLOCKS.containsKey(new ResourceLocation("hbm_m", name)),
                    "Missing block: " + name);
        }
        helper.assertTrue(ForgeRegistries.RECIPE_SERIALIZERS.containsKey(new ResourceLocation("hbm_m", "press")),
                "Missing press recipe serializer");
        long recipes = helper.getLevel().getRecipeManager().getRecipes().stream()
                .filter(recipe -> recipe.getId().getNamespace().equals("hbm_m")).count();
        helper.assertTrue(recipes > 0, "No generated HBM recipes loaded");
        var painting = BuiltInRegistries.PAINTING_VARIANT.getHolderOrThrow(
                ResourceKey.create(Registries.PAINTING_VARIANT, new ResourceLocation("hbm_m", "bober1")));
        helper.assertTrue(painting.is(TagKey.create(Registries.PAINTING_VARIANT,
                new ResourceLocation("minecraft", "placeable"))), "HBM painting is not placeable");
        helper.succeed();
    }

    @GameTest(template = "empty", timeoutTicks = 100)
    public static void batteryLongEnergyAndInventoryRoundTrip(GameTestHelper helper) {
        var state = ModBlocks.MACHINE_BATTERY_SCHRABIDIUM.get().defaultBlockState();
        var original = new MachineBatteryBlockEntity(BlockPos.ZERO, state);
        long expected = 5_000_000_123L; // Above the unsigned 32-bit boundary.
        original.setEnergyStored(expected);
        original.getInventory().setStackInSlot(0, new ItemStack(Items.IRON_INGOT, 7));
        CompoundTag saved = original.saveWithFullMetadata();
        var restored = new MachineBatteryBlockEntity(BlockPos.ZERO, state);
        restored.load(saved);
        helper.assertTrue(restored.getEnergyStored() == expected, "Stored long energy changed on load");
        var stack = restored.getInventory().getStackInSlot(0);
        helper.assertTrue(stack.is(Items.IRON_INGOT) && stack.getCount() == 7, "Inventory changed on load");
        helper.succeed();
    }

    @GameTest(template = "empty", timeoutTicks = 100)
    public static void batteryTicksInServerWorld(GameTestHelper helper) {
        BlockPos relative = new BlockPos(1, 2, 1);
        helper.setBlock(relative, ModBlocks.MACHINE_BATTERY.get().defaultBlockState());
        var entity = helper.getLevel().getBlockEntity(helper.absolutePos(relative));
        helper.assertTrue(entity instanceof MachineBatteryBlockEntity, "Battery block entity not created");
        var battery = (MachineBatteryBlockEntity) entity;
        battery.setEnergyStored(123_456L);
        helper.runAfterDelay(20, () -> {
            helper.assertTrue(!battery.isRemoved(), "Battery removed while ticking");
            helper.assertTrue(battery.getEnergyStored() == 123_456L, "Isolated battery lost/gained energy");
            helper.succeed();
        });
    }
}
