/* SPDX-License-Identifier: LGPL-3.0-only */
package com.hbm.integration.nuclear;

import com.hbm_m.block.ModBlocks;
import com.hbm_m.blockentity.machines.MachineBreederBlockEntity;
import com.hbm_m.blockentity.machines.UniversalMachinePartBlockEntity;
import com.hbm_m.inventory.menu.MachineBreederMenu;
import com.hbm_m.inventory.recipes.BreederRecipes;
import com.hbm_m.item.ModItems;
import com.hbm_m.item.nuclear.BreedingRodItem;
import com.hbm_m.item.nuclear.BreedingRodItem.Size;
import com.hbm_m.item.nuclear.BreedingRodItem.Type;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtIo;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.material.Fluids;
import net.minecraftforge.fluids.FluidStack;
import net.minecraftforge.fluids.capability.IFluidHandler.FluidAction;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import net.minecraftforge.registries.ForgeRegistries;

import com.hbm_m.blockentity.machines.ResearchReactorFluxSource;
import net.minecraft.core.registries.Registries;
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
import net.minecraftforge.registries.RegisterEvent;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

/** Pinned O's float/integer arithmetic, including its 401-tick threshold at nominal flux. */
@GameTestHolder("hbm_m")
@PrefixGameTestTemplate(false)
public final class BreederGameTests {
    private static final BlockPos POS = new BlockPos(2, 1, 2);

    private static ItemStack rod(Size size, Type type) {
        return ((BreedingRodItem) ForgeRegistries.ITEMS.getValue(new ResourceLocation("hbm_m", size.id))).stack(type);
    }

    private static MachineBreederBlockEntity breeder(GameTestHelper helper) {
        return new MachineBreederBlockEntity(helper.absolutePos(POS), ModBlocks.BREEDER.get().defaultBlockState());
    }

    private static BreederTestContent.Source source(GameTestHelper helper, BlockPos relative, int flux) {
        helper.setBlock(relative, BreederTestContent.sourceBlock.defaultBlockState());
        var source = (BreederTestContent.Source) helper.getLevel().getBlockEntity(helper.absolutePos(relative));
        source.flux = flux;
        return source;
    }

    private static void ticks(GameTestHelper helper, MachineBreederBlockEntity breeder, int count) {
        for (int i = 0; i < count; i++) {
            MachineBreederBlockEntity.tick(helper.getLevel(), breeder.getBlockPos(), breeder.getBlockState(), breeder);
        }
    }

    private static void output(GameTestHelper helper, MachineBreederBlockEntity breeder, ItemStack expected, int count) {
        ItemStack stack = breeder.getInventory().getStackInSlot(2);
        helper.assertTrue(count == 0 ? stack.isEmpty() : ItemStack.isSameItemSameTags(stack, expected) && stack.getCount() == count,
                "Unexpected breeder output/count");
    }

    @GameTest(template = "empty")
    public static void breederProcessesRegisteredRecipe(GameTestHelper helper) {
        var source = source(helper, POS.north(), 200);
        var breeder = breeder(helper);
        breeder.getInventory().setStackInSlot(0, rod(Size.SINGLE, Type.LITHIUM));
        ticks(helper, breeder, 400);
        output(helper, breeder, rod(Size.SINGLE, Type.TRITIUM), 0);
        helper.assertTrue(breeder.getProcessProgress() > 0.99F && breeder.getProcessProgress() < 1,
                "O's float accumulation must not round into an early completion");
        ticks(helper, breeder, 1);
        output(helper, breeder, rod(Size.SINGLE, Type.TRITIUM), 1);
        helper.assertTrue(breeder.getInventory().getStackInSlot(0).isEmpty() && breeder.getEnergyStored() == 0
                && breeder.getTank().isEmpty(), "Recipe consumed extra fuel/HE/fluid or failed to consume input");
        ticks(helper, breeder, 600);
        output(helper, breeder, rod(Size.SINGLE, Type.TRITIUM), 1);
        for (int flux : new int[]{399, 400, 600}) {
            source.flux = flux;
            var next = breeder(helper);
            next.getInventory().setStackInSlot(0, rod(Size.SINGLE, Type.LITHIUM));
            int expectedTicks = flux == 399 ? 401 : flux == 400 ? 201 : 134;
            ticks(helper, next, expectedTicks - 1);
            output(helper, next, rod(Size.SINGLE, Type.TRITIUM), 0);
            ticks(helper, next, 1);
            output(helper, next, rod(Size.SINGLE, Type.TRITIUM), 1);
        }
        // Existing flattened IDs remain usable, with O's quad multiplier of THREE.
        var alias = BreederRecipes.getRecipe(new ItemStack(ModItems.ROD_QUAD_NP237.get()));
        helper.assertTrue(alias != null && alias.flux() == 600
                && ItemStack.isSameItemSameTags(alias.result(), rod(Size.QUAD, Type.PU238)), "Existing Np-237 ID changed meaning");
        helper.succeed();
    }

    @GameTest(template = "empty")
    public static void breederStopsWithoutFlux(GameTestHelper helper) {
        var source = source(helper, POS.north(), 199);
        var breeder = breeder(helper);
        breeder.getInventory().setStackInSlot(0, rod(Size.SINGLE, Type.LITHIUM));
        breeder.setEnergyStored(1_000_000); // HE cannot substitute for flux.
        ticks(helper, breeder, 500);
        helper.assertTrue(breeder.getProcessProgress() == 0, "Insufficient flux processed input");
        source.flux = 200;
        ticks(helper, breeder, 200);
        source.flux = 0;
        ticks(helper, breeder, 1);
        helper.assertTrue(breeder.getProcessProgress() == 0, "Flux loss must reset progress");
        source.flux = 200;
        breeder.getInventory().setStackInSlot(2, rod(Size.SINGLE, Type.TRITIUM).copyWithCount(64));
        ticks(helper, breeder, 500);
        output(helper, breeder, rod(Size.SINGLE, Type.TRITIUM), 64);
        helper.assertTrue(breeder.getProcessProgress() == 0, "Full output processed input");
        breeder.getInventory().setStackInSlot(2, rod(Size.SINGLE, Type.CO60));
        ticks(helper, breeder, 500);
        output(helper, breeder, rod(Size.SINGLE, Type.CO60), 1);
        breeder.getInventory().setStackInSlot(2, ItemStack.EMPTY);
        breeder.getInventory().setStackInSlot(0, new ItemStack(Items.DIRT));
        ticks(helper, breeder, 500);
        helper.assertTrue(breeder.getInventory().getStackInSlot(0).is(Items.DIRT), "Wrong input consumed");
        output(helper, breeder, rod(Size.SINGLE, Type.TRITIUM), 0);
        // Space for exactly one result permits stacking, with no overflow.
        breeder.getInventory().setStackInSlot(0, rod(Size.SINGLE, Type.LITHIUM));
        breeder.getInventory().setStackInSlot(2, rod(Size.SINGLE, Type.TRITIUM).copyWithCount(63));
        ticks(helper, breeder, 401);
        output(helper, breeder, rod(Size.SINGLE, Type.TRITIUM), 64);
        helper.succeed();
    }

    @GameTest(template = "empty")
    public static void breederPersistsMidCycle(GameTestHelper helper) throws IOException {
        var source = source(helper, POS.north(), 200);
        var original = breeder(helper);
        original.getInventory().setStackInSlot(0, rod(Size.SINGLE, Type.LITHIUM).copyWithCount(2));
        original.setEnergyStored(123_456);
        original.getTank().fill(new FluidStack(Fluids.WATER, 2345), FluidAction.EXECUTE);
        ticks(helper, original, 177);
        float expected = original.getProcessProgress();
        CompoundTag saved = original.saveWithFullMetadata();
        var bytes = new ByteArrayOutputStream();
        NbtIo.write(saved, new DataOutputStream(bytes));
        var restored = breeder(helper);
        restored.load(NbtIo.read(new DataInputStream(new ByteArrayInputStream(bytes.toByteArray()))));
        helper.assertTrue(Float.floatToIntBits(restored.getProcessProgress()) == Float.floatToIntBits(expected)
                && restored.getFlux() == 200, "Float progress or display flux changed on disk roundtrip");
        helper.assertTrue(original.getInventory().serializeNBT().equals(restored.getInventory().serializeNBT())
                && restored.getEnergyStored() == 123_456 && restored.getTank().getFluidAmount() == 2345,
                "Inventory/HE/tank data changed");
        ticks(helper, restored, 223);
        output(helper, restored, rod(Size.SINGLE, Type.TRITIUM), 0);
        ticks(helper, restored, 1);
        output(helper, restored, rod(Size.SINGLE, Type.TRITIUM), 1);
        helper.assertTrue(restored.getInventory().getStackInSlot(0).getCount() == 1, "Reload duplicated or lost input");
        source.flux = 0;
        restored.load(saved); // Saved flux must never act as a persisted neutron source.
        ticks(helper, restored, 1);
        helper.assertTrue(restored.getFlux() == 0 && restored.getProcessProgress() == 0, "Stale flux resumed processing");
        for (float value : new float[]{Float.NaN, Float.POSITIVE_INFINITY, -1, 1}) {
            saved.putFloat("progress", value);
            restored.load(saved);
            helper.assertTrue(restored.getProcessProgress() == 0, "Invalid progress loaded");
        }
        saved.putInt("progress", 599); // Historical M scaffold format, not normalized O progress.
        restored.load(saved);
        helper.assertTrue(restored.getProcessProgress() == 0, "Legacy integer progress became a free recipe");
        helper.succeed();
    }

    @GameTest(template = "empty")
    public static void breederDefaultRecipeVariants(GameTestHelper helper) {
        Type[] inputs = {Type.LITHIUM, Type.CO, Type.RA226, Type.TH232, Type.U235, Type.NP237, Type.PU238, Type.U238, Type.URANIUM, Type.RGP};
        Type[] outputs = {Type.TRITIUM, Type.CO60, Type.AC227, Type.THF, Type.NP237, Type.PU238, Type.PU239, Type.RGP, Type.RGP, Type.WASTE};
        int[] flux = {200, 100, 300, 500, 300, 200, 1000, 300, 200, 200};
        int[] multipliers = {1, 2, 3}; // Independent O oracle, especially quad != four.
        int recipes = 0;
        for (Size size : Size.values()) for (int i = 0; i < inputs.length; i++) {
            var recipe = BreederRecipes.getRecipe(rod(size, inputs[i]));
            helper.assertTrue(recipe != null && recipe.flux() == flux[i] * multipliers[size.ordinal()]
                    && ItemStack.isSameItemSameTags(recipe.result(), rod(size, outputs[i])), "Incorrect O rod recipe/flux");
            recipes++;
        }
        var sword = BreederRecipes.getRecipe(new ItemStack(ForgeRegistries.ITEMS.getValue(BreederRecipes.SWORD_INPUT)));
        helper.assertTrue(sword != null && sword.flux() == 1000
                && sword.result().is(ForgeRegistries.ITEMS.getValue(BreederRecipes.SWORD_OUTPUT)), "Incorrect O sword recipe");
        helper.assertTrue(recipes + 1 == 31 && BreederRecipes.getRecipe(rod(Size.SINGLE, Type.LEAD)) == null,
                "Missing or invented default recipe");
        ItemStack malformed = rod(Size.SINGLE, Type.LITHIUM);
        malformed.getOrCreateTag().putString("breedingType", "INVALID");
        helper.assertTrue(BreederRecipes.getRecipe(malformed) == null, "Invalid rod variant accepted");
        helper.succeed();
    }

    @GameTest(template = "empty")
    public static void breederReadsHorizontalResearchContacts(GameTestHelper helper) {
        var breeder = breeder(helper);
        source(helper, POS.above(), 1000);
        ticks(helper, breeder, 1);
        helper.assertTrue(breeder.getFlux() == 0, "Vertical source counted");
        var core = source(helper, POS.east(), 123);
        source(helper, POS.west(), 77);
        ticks(helper, breeder, 1);
        helper.assertTrue(breeder.getFlux() == 200, "Horizontal source sum changed");
        helper.setBlock(POS.north(), ModBlocks.UNIVERSAL_MACHINE_PART.get().defaultBlockState());
        var part = (UniversalMachinePartBlockEntity) helper.getLevel().getBlockEntity(helper.absolutePos(POS.north()));
        part.setControllerPos(core.getBlockPos());
        ticks(helper, breeder, 1);
        helper.assertTrue(breeder.getFlux() == 323, "Research-core part not resolved per contacting face");
        helper.setBlock(POS.east(), Blocks.AIR);
        ticks(helper, breeder, 1);
        helper.assertTrue(breeder.getFlux() == 77, "Removed or stale research core still supplied flux");
        helper.succeed();
    }

    @GameTest(template = "empty")
    public static void breederSynchronizesTwoObservers(GameTestHelper helper) {
        source(helper, POS.north(), 100_123); // Above unsigned 16-bit boundary.
        var server = breeder(helper);
        server.getInventory().setStackInSlot(0, rod(Size.SINGLE, Type.LITHIUM));
        ticks(helper, server, 1);
        var first = breeder(helper);
        var second = breeder(helper);
        ClientboundBlockEntityDataPacket packet = ClientboundBlockEntityDataPacket.create(server);
        first.onDataPacket(null, packet);
        second.onDataPacket(null, packet);
        helper.assertTrue(first.getUpdateTag().equals(second.getUpdateTag()) && first.getFlux() == 100_123
                && first.getProcessProgress() == server.getProcessProgress(), "S2C observers diverged");
        for (int i = 0; i < MachineBreederBlockEntity.DATA_COUNT; i++) {
            // Vanilla container data travels as signed shorts; test those actual truncation rules.
            first.getContainerData().set(i, (short) server.getContainerData().get(i));
        }
        helper.assertTrue(first.getFlux() == 100_123, "Menu lost high flux bits");
        var player = net.minecraftforge.common.util.FakePlayerFactory.getMinecraft(helper.getLevel());
        var firstMenu = new MachineBreederMenu(1, player.getInventory(), first);
        var secondMenu = new MachineBreederMenu(2, player.getInventory(), second);
        helper.assertTrue(firstMenu.getFlux() == 100_123 && secondMenu.getFlux() == 100_123,
                "Open menu observers lost flux");
        helper.assertTrue(!firstMenu.getSlot(0).mayPlace(new ItemStack(Items.DIRT))
                && !firstMenu.getSlot(2).mayPlace(rod(Size.SINGLE, Type.TRITIUM)), "Menu slot filters bypassed");
        // This is a transport roundtrip, not two connected production clients (G5).
        helper.succeed();
    }

    @GameTest(template = "empty", timeoutTicks = 60)
    public static void breederTicksInServerWorld(GameTestHelper helper) {
        helper.setBlock(POS, ModBlocks.BREEDER.get().defaultBlockState());
        var breeder = (MachineBreederBlockEntity) helper.getLevel().getBlockEntity(helper.absolutePos(POS));
        source(helper, POS.north(), 200);
        breeder.getInventory().setStackInSlot(0, rod(Size.SINGLE, Type.LITHIUM));
        helper.runAfterDelay(10, () -> {
            helper.assertTrue(!breeder.isRemoved() && breeder.getProcessProgress() > 0 && breeder.getFlux() == 200,
                    "Registered breeder did not tick beside its research source");
            helper.assertTrue(helper.getBlockState(POS.above()).is(ModBlocks.UNIVERSAL_MACHINE_PART.get())
                    && helper.getBlockState(POS.above(2)).is(ModBlocks.UNIVERSAL_MACHINE_PART.get()),
                    "Original three-high footprint failed to form");
            helper.succeed();
        });
    }

    @GameTest(template = "empty")
    public static void breederRequiresProductionBindings(GameTestHelper helper) {
        helper.assertTrue(!BreederTestContent.suppliedMissingItems,
                "R-N01-breeding-rods unresolved: test-only item fixtures were needed; production feature BLOCKED");
        helper.assertTrue(ModBlocks.REACTOR_SMALL.get() instanceof EntityBlock,
                "N-05 unresolved: reactor_small is a generic block, not a simulated research flux source");
        helper.succeed();
    }

    /** Test-only source and missing-item fixtures; required production-binding test prevents false green G3. */
    @Mod.EventBusSubscriber(modid = "hbm_m", bus = Mod.EventBusSubscriber.Bus.MOD)
    public static final class BreederTestContent {
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
}
