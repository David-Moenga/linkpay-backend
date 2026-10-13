from django.contrib import admin

from .models import AuditLog, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in Transaction._meta.fields]
    list_display = ("reference", "transaction_type", "status", "amount", "currency", "sender", "recipient", "created_at")
    search_fields = ("reference", "sender__username", "recipient__username")
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
