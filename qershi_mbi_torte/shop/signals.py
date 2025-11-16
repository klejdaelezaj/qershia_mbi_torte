from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderNotification

@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    if not created:
        if instance.status == "preparing":
            message = (
                "👩‍🍳 Porosia juaj është marrë me sukses! "
                "Shefat tanë po e përgatisin me dashuri që të vijë perfekte tek ju. 🍒"
            )

        elif instance.status == "shipped":
            message = (
                "🏍 Korrieri ynë sapo mori porosinë tuaj! "
                "Brenda 30 minutash, ëmbëlsira juaj do të jetë pranë jush. 🍰"
            )

        # 3️⃣ Porosia u dorëzua me sukses
        elif instance.status == "delivered":
            message = (
                "Porosia juaj u dorëzua me sukses "
                "Shijoni copën tuaj të ëmbël nga ‘Qershia mbi Tortë’. Faleminderit që na zgjodhët! ❤️"
            )

        else:
            message = f"ℹ️ Statusi i porosisë ndryshoi në: {instance.status}"

        # krijo njoftimin vetëm nëse nuk ekziston më parë
        if not OrderNotification.objects.filter(
            user=instance.user,
            order=instance,
            message=message
        ).exists():
            OrderNotification.objects.create(
                user=instance.user,
                order=instance,
                message=message
            )
