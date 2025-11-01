from django.contrib import admin
from .models import Hospital, Patient, Doctor, Resource
from allocation.utils import run_allocation

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'top_priority_avaiable_beds',
                    'mid_priority_avaiable_beds', 'low_priority_avaiable_beds', 'total_beds')
    search_fields = ('name', 'location')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'address', 'email', 'emargency_contact', 'get_priority_level', 'hospital_name')
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
