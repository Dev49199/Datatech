from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required,user_passes_test
# Create your views here.
from .models import Article,Customer
import stripe
from .forms import CustomSignUpForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import authenticate,login
from django.http import HttpResponse

stripe.api_key = "sk_test_SlpZcoGj69OpZyHpy75H2BcD00RBx5clze"


def home(request):
	articles = Article.objects
	return render(request,'plans/home.html',{'plans':articles})




def plan(request,pk):
	plan = get_object_or_404(Article,pk=pk)
	if plan.premium:
		if request.user.is_authenticated:
			try:
				if request.user.customer.membership:
					return render(request,"plans/plan.html",{'plan':plan})
			except Customer.DoesNotExist:
				return redirect('join')
	else:
		return render(request,'plans/plan.html',{'plan':plan})



def join(request):
	return render(request,'plans/join.html')


@login_required
def checkout(request):
	try:
		if request.user.customer.membership:
			return redirect('settings')
	except Customer.DoesNotExist:
		pass

	coupons ={'diwali10':10,'dhamaka':30}

	if request.method=='POST':
		stripe_customer = stripe.Customer.create(email=request.user.email,
			source = request.POST['stripeToken'])
		plan = 'plan_FsoKd9AiwcPXWr'
		if request.POST['plan']=='yearly':
			plan = 'plan_FsoPEOmuysWw1X'


		if request.POST['coupon'] in coupons:
			percentage = coupons[request.POST['coupon'].lower()]
			try:
				coupon = stripe.Coupon.create(duration='once',id=request.POST['coupon'].lower(),
					percentage_off=percentage)
			except:
				pass
			subscription = stripe.Subscription.create(customer=stripe_customer.id,items=[{'plan':plan}],coupon = request.POST['coupon'].lower())

		else:
			subscription = stripe.Subscription.create(customer=stripe_customer.id,
				items=[{'plan':plan}])

		customer = Customer()
		customer.user = request.user
		customer.stripeid = stripe_customer.id
		customer.membership=True
		customer.cancel_at_period_end = False
		customer.stripe_subscription_id = subscription.id
		customer.save()


	else:
		coupon = 'None'
		plan='monthly'
		price = 1000
		og_dollar = 10
		coupon_dollar = 0
		final_dollar = 10

		if request.method=='GET' and plan in request.GET:
			if request.GET['plan']=='yearly':
				plan = 'plan_FsoPEOmuysWw1X'
				price = 10000
				og_dollar = 100
				final_dollar = 100


		if request.method=='GET' and 'coupon' in request.GET:
			if request.GET['coupon'].lower() in coupons:
				coupon = request.GET['coupon'].lower()
				percentage = coupons[request.GET['coupon'].lower()]

				coupon_price = int((percentage/100)*price)
				price = price - coupon_price
				coupon_dollar = str(coupon_price)[:-2] + '.' + str(coupon_price)[-2:]
				final_dollar = str(price)[:-2] + '.' + str(price)[-2:]
		return render(request,'plans/checkout.html',{'plan':plan,'coupon':coupon,'price':price,'og_dollar':og_dollar,
        'coupon_dollar':coupon_dollar,'final_dollar':final_dollar})





def settings(request):
	membership=False
	cancel_at_period_end=False
	if request.method=='POST':
		subscription = stripe.Subscription.retrieve(request.user.customer.stripe_subscription_id)
		subscription.cancel_at_period_end=True
		request.user.customer.cancel_at_period_end=True
		subscription.save()
		request.user.customer.save()
	else:
		try:
			if request.user.customer.membership:
				membership=True
			if request.user.customer.cancel_at_period_end:
				cancel_at_period_end=True
		except Customer.DoesNotExist:
			membership=False
		return render(request, 'registration/settings.html', {'membership':membership,
    'cancel_at_period_end':cancel_at_period_end})





@user_passes_test(lambda u:u.is_superuser)
def updateaccounts(request):
	customers = Customer.objects.all()
	for customer in customers:
		subscription = stripe.Subscription.retrieve(customer.stripe_subscription_id)
		if subscription.status!='active':
			customer.membership=False
		else:
			customer.membership=True
		customer.cancel_at_period_end=subscription.cancel_at_period_end
		customer.save()

	return HttpResponse("Accounts Update Completed")





class SignUp(CreateView):
	form_class = CustomSignUpForm
	success_url = reverse_lazy('home')
	template_name = "registration/signup.html"


	def form_valid(self,form):
		valid = super(SignUp,self).form_valid(form)
		username,password = form.cleaned_data.get('username'),form.cleaned_data.get('password1')
		new_user = authenticate(username=username,password=password)
		login(self.request,new_user)
		return valid



			

