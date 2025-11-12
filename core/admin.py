from django.contrib import admin , messages
from .models import  Resource, TransportFlow, supply_max_cap
from allocation.utils import run_supply_optimization, calculate_single_pair_flow


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'volume', 'priority_score')
    search_fields = ('name',)
    list_filter = ('priority_score',)
    actions = ['run_optimize'] 

    def run_optimize(self, request, queryset):
        selected, total_value = run_supply_optimization()
        selected_names = ", ".join([item.name for item in selected])
        self.message_user(
            request,
            f"✅ Optimization complete. Total utility: {total_value}. Selected: {selected_names}"
        )
    run_optimize.short_description = "Run Resource Optimization (Knapsack)"


@admin.register(TransportFlow)
class TransportFlowAdmin(admin.ModelAdmin):
    # 'amount_sent' is no longer needed here, but you can keep it
    list_display = ("A", "to", "max_capacity", "amount_sent")
    search_fields = ("A", "to")
    actions = ["calculate_max_flow_for_selected"] # Changed this line

    def calculate_max_flow_for_selected(self, request, queryset):
        """
        Admin action to calculate max-flow for a single selected route.
        """
        # 1. Check that the user selected only ONE route
        if queryset.count() != 1:
            messages.error(request, "Please select exactly one route to test.")
            return

        selected_route = queryset.first()
        source_node = selected_route.A
        sink_node = selected_route.to

        # 2. Call your new utility function
        try:
            total_flow = calculate_single_pair_flow(source_node, sink_node)
            messages.success(
                request, 
                f"✅ Total Max Flow from '{source_node}' to '{sink_node}' is: {total_flow} units"
            )
        except Exception as e:
            messages.error(request, f"❌ Error during calculation: {e}")

    calculate_max_flow_for_selected.short_description = "Calculate Max Flow (Source → Sink)"

# You will also need to register your other models here (Supply_center, etc.)
# so you can populate them for your *other* algorithm.

@admin.register(supply_max_cap)
class SupplyMaxCapAdmin(admin.ModelAdmin):
    list_display = ('id', 'capacity')