/* SPDX-License-Identifier: GPL-3.0-only
 * N-01, 2026-10-20. New adapter for all default breeder recipes from
 * HBM, The Bobcat and contributors, aee05a40f10fb7bb9b042b65eccaa449ecc1672d.
 */
package com.hbm_m.inventory.recipes;

import com.hbm_m.item.ModItems;
import com.hbm_m.item.nuclear.BreedingRodItem;
import com.hbm_m.item.nuclear.BreedingRodItem.Size;
import com.hbm_m.item.nuclear.BreedingRodItem.Type;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

public final class BreederRecipes {
    public static final ResourceLocation SWORD_INPUT = new ResourceLocation("hbm_m", "meteorite_sword_etched");
    public static final ResourceLocation SWORD_OUTPUT = new ResourceLocation("hbm_m", "meteorite_sword_bred");

    private BreederRecipes() { }

    public record Recipe(ItemStack result, int flux) { }

    public static Recipe getRecipe(ItemStack input) {
        if (input.isEmpty()) return null;
        if (ForgeRegistries.ITEMS.containsKey(SWORD_INPUT) && ForgeRegistries.ITEMS.containsKey(SWORD_OUTPUT)
                && input.is(ForgeRegistries.ITEMS.getValue(SWORD_INPUT))) {
            return new Recipe(new ItemStack(ForgeRegistries.ITEMS.getValue(SWORD_OUTPUT)), 1000);
        }
        Type type;
        Size size;
        if (input.getItem() instanceof BreedingRodItem rod) {
            type = BreedingRodItem.type(input);
            size = rod.size();
        } else if (input.is(ModItems.ROD_QUAD_NP237.get())) {
            type = Type.NP237;
            size = Size.QUAD;
        } else if (input.is(ModItems.ROD_QUAD_URANIUM.get())) {
            type = Type.URANIUM;
            size = Size.QUAD;
        } else {
            return null;
        }
        if (type == null) return null;
        Type result;
        int flux;
        switch (type) {
            case LITHIUM -> { result = Type.TRITIUM; flux = 200; }
            case CO -> { result = Type.CO60; flux = 100; }
            case RA226 -> { result = Type.AC227; flux = 300; }
            case TH232 -> { result = Type.THF; flux = 500; }
            case U235 -> { result = Type.NP237; flux = 300; }
            case NP237 -> { result = Type.PU238; flux = 200; }
            case PU238 -> { result = Type.PU239; flux = 1000; }
            case U238 -> { result = Type.RGP; flux = 300; }
            case URANIUM -> { result = Type.RGP; flux = 200; }
            case RGP -> { result = Type.WASTE; flux = 200; }
            default -> { return null; }
        }
        ResourceLocation outputId = new ResourceLocation("hbm_m", size.id);
        if (!ForgeRegistries.ITEMS.containsKey(outputId)
                || !(ForgeRegistries.ITEMS.getValue(outputId) instanceof BreedingRodItem output)
                || output.size() != size) return null;
        return new Recipe(output.stack(result), flux * size.fluxMultiplier);
    }
}
