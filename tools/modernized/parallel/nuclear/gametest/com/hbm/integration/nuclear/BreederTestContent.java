/* SPDX-License-Identifier: LGPL-3.0-only */
package com.hbm.integration.nuclear;

import com.hbm_m.blockentity.machines.ResearchReactorFluxSource;
import com.hbm_m.inventory.recipes.BreederRecipes;
import com.hbm_m.item.nuclear.BreedingRodItem;
import com.hbm_m.item.nuclear.BreedingRodItem.Size;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegisterEvent;

/** Test-only source and missing-item fixtures; required production-binding test prevents false green G3. */
@Mod.EventBusSubscriber(modid = "hbm_m", bus = Mod.EventBusSubscriber.Bus.MOD)
public final class BreederTestContent {
    static SourceBlock sourceBlock;
    static BlockEntityType<Source> sourceType;
    static boolean suppliedMissingItems;

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void register(RegisterEvent event) {
        event.register(Registries.BLOCK, helper -> {
            sourceBlock = new SourceBlock();
            helper.register(new ResourceLocation("hbm_m", "nuclear_test_flux_source"), sourceBlock);
        });
        event.register(Registries.BLOCK_ENTITY_TYPE, helper -> {
            sourceType = BlockEntityType.Builder.of(Source::new, sourceBlock).build(null);
            helper.register(new ResourceLocation("hbm_m", "nuclear_test_flux_source"), sourceType);
        });
        if (!event.getRegistryKey().equals(Registries.ITEM)) return;
        for (Size size : Size.values()) {
            ResourceLocation id = new ResourceLocation("hbm_m", size.id);
            if (!ForgeRegistries.ITEMS.containsKey(id)) {
                suppliedMissingItems = true;
                event.register(Registries.ITEM, helper -> helper.register(id, new BreedingRodItem(new Item.Properties(), size)));
            }
        }
        for (ResourceLocation id : new ResourceLocation[]{BreederRecipes.SWORD_INPUT, BreederRecipes.SWORD_OUTPUT}) {
            if (!ForgeRegistries.ITEMS.containsKey(id)) {
                suppliedMissingItems = true;
                event.register(Registries.ITEM, helper -> helper.register(id, new Item(new Item.Properties().stacksTo(1))));
            }
        }
    }

    static final class SourceBlock extends BaseEntityBlock {
        SourceBlock() { super(BlockBehaviour.Properties.of()); }
        @Override public BlockEntity newBlockEntity(BlockPos pos, BlockState state) { return new Source(pos, state); }
        @Override public RenderShape getRenderShape(BlockState state) { return RenderShape.MODEL; }
    }

    static final class Source extends BlockEntity implements ResearchReactorFluxSource {
        int flux;
        Source(BlockPos pos, BlockState state) { super(sourceType, pos, state); }
        @Override public int getTotalFlux() { return flux; }
    }
}
