from django.contrib import admin , messages
from .models import Hospital, Patient, Doctor, Resource, HospitalTransfer, Supply_center, Disaster_zone, TransportFlow
from allocation.utils import run_allocation, run_transport_allocation


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'top_priority_avaiable_beds',
                    'mid_priority_avaiable_beds', 'low_priority_avaiable_beds', 'total_beds')
    search_fields = ('name', 'location')

@admin.register(HospitalTransfer)
class HospitalTransferAdmin(admin.ModelAdmin):
    list_display = ('from_hospital', 'to_hospital' , 'capacity')
    search_fields = ('from_hospital__name', 'to_hospital__name')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'address', 'email', 'emergency_contact', 'get_priority_level', 'hospital_name')
    list_filter = ('priority_level', 'hospital_name')
    search_fields = ('name', 'email', 'address')
    actions = ['run_auto_allocation'] 

    def run_auto_allocation(self, request, queryset):
        run_allocation()  # Call your allocation logic
        self.message_user(request, "✅ Allocation complete.")

    run_auto_allocation.short_description = "Run Auto-Allocation" 

    def get_priority_level(self, obj):
        return obj.get_priority_level_display()
    get_priority_level.short_description = 'Priority Level'


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'spaciality', 'avaiable')
    list_filter = ('avaiable', 'spaciality')
    search_fields = ('name', 'spaciality')

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'priority_score')
    search_fields = ('name',)
    list_filter = ('priority_score',)
    actions = ['run_optimize'] 

    def run_optimize(self, request, queryset):
        max_capacity = 50  # You can adjust this or make it dynamic
        from allocation.knapsack import run_knapsack # import your knapsack function
        max_capacity = sum(resource.quantity for resource in queryset)
        selected, total_value = run_knapsack(max_capacity)
        
        # Optionally, display the selected items in the Django admin message
        selected_names = ", ".join([item.name for item in selected])
        self.message_user(
            request,
            f"✅ Optimization complete. Total utility: {total_value}. Selected: {selected_names}"
        )

    run_optimize.short_description = "Run Resource Optimization (Knapsack)"

@admin.register(Supply_center)
class Supply_center_Admin(admin.ModelAdmin):
    list_display = ('name','total_stock')
    search_fields = ('name',)

@admin.register(Disaster_zone)
class Disaster_zone_Admin(admin.ModelAdmin):
    list_display = ('name','demand')
    search_fields = ('name',)


@admin.action(description="🚚 Allocate Transport")
def allocate_selected_transport(modeladmin, request, queryset):
    """
    Admin action to allocate transport for selected TransportFlow objects
    """
    try:
        # Here you can call your existing logic
        run_transport_allocation()  # run allocation for all transport
        messages.success(request, "✅ Transport allocation executed successfully!")
    except Exception as e:
        messages.error(request, f"❌ Error during allocation: {e}")

@admin.register(TransportFlow)
class TransportFlowAdmin(admin.ModelAdmin):
    list_display = ("center", "zone", "amount_sent")
    actions = [allocate_selected_transport]


