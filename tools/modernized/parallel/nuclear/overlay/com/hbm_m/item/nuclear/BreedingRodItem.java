/* SPDX-License-Identifier: GPL-3.0-only
 * N-01, 2026-10-20. New 1.20.1 representation of the pinned O breeding-rod
 * metadata variants (HBM, The Bobcat and contributors). No texture bytes copied.
 */
package com.hbm_m.item.nuclear;

import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

public final class BreedingRodItem extends Item {
    public enum Type {
        LITHIUM, TRITIUM, CO, CO60, TH232, THF, U235, NP237, U238,
        PU238, PU239, RGP, WASTE, LEAD, URANIUM, RA226, AC227
    }

    public enum Size {
        SINGLE("rod", 1), DUAL("rod_dual", 2), QUAD("rod_quad", 3);
        public final String id;
        public final int fluxMultiplier;
        Size(String id, int fluxMultiplier) {
            this.id = id;
            this.fluxMultiplier = fluxMultiplier;
        }
    }

    private final Size size;

    public BreedingRodItem(Properties properties, Size size) {
        super(properties);
        this.size = size;
    }

    public Size size() { return size; }

    public static Type type(ItemStack stack) {
        if (!(stack.getItem() instanceof BreedingRodItem)) return null;
        if (stack.getTag() == null || !stack.getTag().contains("breedingType")) return Type.LITHIUM;
        try { return Type.valueOf(stack.getTag().getString("breedingType")); }
        catch (IllegalArgumentException invalid) { return null; }
    }

    public ItemStack stack(Type type) {
        ItemStack result = new ItemStack(this);
        // No tag is the original metadata-zero lithium variant.
        if (type != Type.LITHIUM) result.getOrCreateTag().putString("breedingType", type.name());
        return result;
    }
}
