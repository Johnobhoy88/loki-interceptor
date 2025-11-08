# B2B SaaS Development

Expert in architecting LOKI as a B2B SaaS compliance platform.

## SaaS Architecture Overview

### Multi-Tenancy Model

**Database-per-Tenant** (Recommended for compliance)
```python
# Separate databases for data isolation and compliance
TENANT_DATABASES = {
    'tenant_acme': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'loki_tenant_acme',
        'HOST': 'db-cluster.region.rds.amazonaws.com',
    },
    'tenant_globex': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'loki_tenant_globex',
        'HOST': 'db-cluster.region.rds.amazonaws.com',
    },
}

# Benefits:
# - Complete data isolation (critical for compliance)
# - Easier GDPR compliance (tenant data deletion)
# - Independent scaling per tenant
# - Regulatory compliance (FCA, SOC 2)
```

**Schema-per-Tenant** (Alternative)
```python
# Shared database, separate schemas
class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = self.get_tenant_from_request(request)
        set_schema(tenant.schema_name)
        response = self.get_response(request)
        return response

# Benefits:
# - More cost-effective
# - Easier maintenance
# - Drawbacks: Less isolation, harder compliance
```

### API Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│    (Rate Limiting, Authentication, Routing)                  │
└─────────────────────────────────────────────────────────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
┌───▼───┐          ┌──────▼──────┐      ┌──────▼──────┐
│Tenant │          │ Validation  │      │ Correction  │
│  Mgmt │          │   Service   │      │  Service    │
└───────┘          └─────────────┘      └─────────────┘
                          │
                   ┌──────▼──────┐
                   │   Modules   │
                   │  (FCA, GDPR,│
                   │  Tax, etc.) │
                   └─────────────┘
```

## Tenant Management

### Tenant Model

```python
from django.db import models
from django.contrib.postgres.fields import JSONField

class Tenant(models.Model):
    """
    Represents a B2B customer organization
    """
    # Identity
    tenant_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    # Subscription
    plan = models.CharField(max_length=50, choices=[
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ])
    subscription_status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ])

    # Configuration
    enabled_modules = models.JSONField(default=list)  # ['fca_uk', 'gdpr_uk']
    api_quota = models.IntegerField()  # Requests per month
    max_users = models.IntegerField()

    # Billing
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    billing_email = models.EmailField()

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class TenantUser(models.Model):
    """
    User belonging to a tenant
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('user', 'User'),
        ('readonly', 'Read-Only'),
    ])
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('tenant', 'user')
```

### Tenant Isolation

```python
class TenantAwareQuerySet(models.QuerySet):
    """
    Automatically filter queries by current tenant
    """
    def for_tenant(self, tenant):
        return self.filter(tenant=tenant)

class TenantAwareManager(models.Manager):
    def get_queryset(self):
        tenant = get_current_tenant()
        return super().get_queryset().filter(tenant=tenant)

class ValidationHistory(models.Model):
    """
    Store validation history per tenant
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50)
    modules_used = models.JSONField()
    status = models.CharField(max_length=10)  # PASS/FAIL
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantAwareManager()

    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'created_at']),
        ]
```

## Subscription Management

### Plan Tiers

```python
SUBSCRIPTION_PLANS = {
    'starter': {
        'name': 'Starter',
        'price_monthly': 99,  # GBP
        'price_annual': 990,  # 2 months free
        'features': {
            'api_quota': 10000,  # requests/month
            'max_users': 3,
            'modules': ['fca_uk', 'gdpr_uk'],
            'support': 'email',
            'sla': '99%',
        },
    },
    'professional': {
        'name': 'Professional',
        'price_monthly': 299,
        'price_annual': 2990,
        'features': {
            'api_quota': 50000,
            'max_users': 10,
            'modules': ['fca_uk', 'gdpr_uk', 'tax_uk', 'nda_uk', 'hr_scottish'],
            'support': 'priority_email',
            'sla': '99.5%',
            'custom_gates': True,
        },
    },
    'enterprise': {
        'name': 'Enterprise',
        'price_monthly': 'custom',
        'price_annual': 'custom',
        'features': {
            'api_quota': 'unlimited',
            'max_users': 'unlimited',
            'modules': 'all',
            'support': 'dedicated',
            'sla': '99.9%',
            'custom_gates': True,
            'white_label': True,
            'on_premise': 'optional',
        },
    },
}
```

### Stripe Integration

```python
import stripe

class SubscriptionManager:
    def __init__(self, stripe_api_key):
        stripe.api_key = stripe_api_key

    def create_subscription(self, tenant, plan_id, payment_method):
        """
        Create Stripe subscription for tenant

        Args:
            tenant: Tenant model instance
            plan_id: Plan identifier
            payment_method: Stripe payment method ID

        Returns:
            dict: Subscription details
        """
        # Create or retrieve Stripe customer
        if not tenant.stripe_customer_id:
            customer = stripe.Customer.create(
                email=tenant.billing_email,
                name=tenant.name,
                metadata={'tenant_id': tenant.tenant_id}
            )
            tenant.stripe_customer_id = customer.id
            tenant.save()
        else:
            customer = stripe.Customer.retrieve(tenant.stripe_customer_id)

        # Attach payment method
        stripe.PaymentMethod.attach(
            payment_method,
            customer=customer.id
        )

        # Set as default
        stripe.Customer.modify(
            customer.id,
            invoice_settings={'default_payment_method': payment_method}
        )

        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': PLAN_PRICE_IDS[plan_id]}],
            metadata={'tenant_id': tenant.tenant_id}
        )

        # Update tenant
        tenant.plan = plan_id
        tenant.subscription_status = 'active'
        tenant.save()

        return subscription

    def handle_webhook(self, event):
        """
        Handle Stripe webhooks

        Event types:
        - customer.subscription.updated
        - customer.subscription.deleted
        - invoice.payment_failed
        """
        event_type = event['type']
        data = event['data']['object']

        if event_type == 'customer.subscription.updated':
            self._update_subscription(data)
        elif event_type == 'customer.subscription.deleted':
            self._cancel_subscription(data)
        elif event_type == 'invoice.payment_failed':
            self._handle_payment_failure(data)

    def _update_subscription(self, subscription_data):
        tenant = Tenant.objects.get(stripe_customer_id=subscription_data['customer'])
        tenant.subscription_status = subscription_data['status']
        tenant.save()
```

## Usage Tracking & Analytics

### API Usage Tracking

```python
class UsageTracker:
    def __init__(self, tenant):
        self.tenant = tenant
        self.redis = redis.Redis()

    def track_api_call(self, endpoint, module, status):
        """
        Track API usage for quota enforcement and billing

        Args:
            endpoint: API endpoint called
            module: Compliance module used
            status: 'success' or 'error'
        """
        # Increment counters
        month_key = f"usage:{self.tenant.tenant_id}:{datetime.now().strftime('%Y-%m')}"

        self.redis.hincrby(month_key, 'total_requests', 1)
        self.redis.hincrby(month_key, f'module:{module}', 1)
        self.redis.hincrby(month_key, f'status:{status}', 1)

        # Set expiry (3 months)
        self.redis.expire(month_key, 3600 * 24 * 90)

        # Check quota
        usage = self.redis.hget(month_key, 'total_requests')
        if int(usage) > self.tenant.api_quota:
            raise QuotaExceededError(
                f"Monthly quota of {self.tenant.api_quota} requests exceeded"
            )

    def get_usage_stats(self, month=None):
        """
        Get usage statistics for billing/analytics

        Returns:
            dict: Usage breakdown
        """
        if month is None:
            month = datetime.now().strftime('%Y-%m')

        month_key = f"usage:{self.tenant.tenant_id}:{month}"
        data = self.redis.hgetall(month_key)

        return {
            'month': month,
            'total_requests': int(data.get(b'total_requests', 0)),
            'by_module': {
                module.decode(): int(count)
                for key, count in data.items()
                if key.startswith(b'module:')
                for module in [key.replace(b'module:', b'')]
            },
            'success_rate': self._calculate_success_rate(data),
        }
```

### Analytics Dashboard

```python
class TenantAnalytics:
    def __init__(self, tenant):
        self.tenant = tenant

    def get_dashboard_data(self, start_date, end_date):
        """
        Generate analytics dashboard data

        Returns:
            dict: Dashboard metrics
        """
        validations = ValidationHistory.objects.filter(
            tenant=self.tenant,
            created_at__range=(start_date, end_date)
        )

        return {
            'total_validations': validations.count(),
            'pass_rate': self._calculate_pass_rate(validations),
            'top_violations': self._get_top_violations(validations),
            'by_document_type': self._group_by_document_type(validations),
            'by_module': self._group_by_module(validations),
            'compliance_trend': self._calculate_trend(validations),
        }

    def _get_top_violations(self, validations):
        """Find most common gate failures"""
        from collections import Counter

        all_failures = []
        for validation in validations:
            if validation.status == 'FAIL':
                failed_gates = self._extract_failed_gates(validation)
                all_failures.extend(failed_gates)

        return Counter(all_failures).most_common(10)
```

## Customer Onboarding

### Onboarding Workflow

```python
class OnboardingManager:
    def __init__(self, tenant):
        self.tenant = tenant

    def create_onboarding_checklist(self):
        """
        Create onboarding tasks for new tenant

        Returns:
            list: Onboarding steps
        """
        return [
            {
                'step': 1,
                'title': 'Create Account',
                'status': 'complete',
                'description': 'Account created successfully',
            },
            {
                'step': 2,
                'title': 'Choose Plan',
                'status': 'complete',
                'description': f'Subscribed to {self.tenant.plan} plan',
            },
            {
                'step': 3,
                'title': 'Add Team Members',
                'status': 'pending',
                'action': 'invite_users',
                'description': 'Invite your team members',
            },
            {
                'step': 4,
                'title': 'Configure Modules',
                'status': 'pending',
                'action': 'select_modules',
                'description': 'Choose compliance modules for your needs',
            },
            {
                'step': 5,
                'title': 'API Integration',
                'status': 'pending',
                'action': 'get_api_key',
                'description': 'Get API key and integrate LOKI',
            },
            {
                'step': 6,
                'title': 'First Validation',
                'status': 'pending',
                'action': 'test_validation',
                'description': 'Validate your first document',
            },
        ]

    def send_onboarding_email(self, step):
        """Send onboarding emails based on step"""
        templates = {
            'welcome': 'emails/onboarding_welcome.html',
            'api_setup': 'emails/onboarding_api.html',
            'first_validation': 'emails/onboarding_first_validation.html',
        }
        # Send email logic here
```

## Best Practices

1. **Data Isolation** - Use database-per-tenant for compliance
2. **Quota Enforcement** - Track and enforce API quotas
3. **Usage Metering** - Accurate billing requires accurate tracking
4. **Audit Logging** - Log all tenant actions for compliance
5. **Multi-Region** - Deploy in multiple regions for performance
6. **Automated Backups** - Per-tenant backup strategy
7. **SOC 2 Compliance** - Follow SOC 2 Type II requirements
8. **GDPR Compliance** - Tenant data deletion within 30 days
9. **Graceful Degradation** - Handle quota exceeded gracefully
10. **Customer Success** - Proactive monitoring and support

## Resources

- Tenant management: `backend/saas/tenants/`
- Billing integration: `backend/saas/billing/`
- Analytics: `backend/saas/analytics/`
- Onboarding: `backend/saas/onboarding/`

## See Also

- `multi-tenancy.md` - Tenant isolation patterns
- `billing.md` - Subscription and payment management
- `analytics.md` - Usage tracking and reporting
- `customer-management.md` - Onboarding and support workflows
