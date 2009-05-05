# django imports
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext

# reviews imports
from reviews.models import Review

class ReviewForm(ModelForm):
    """Form to manage/edit a review.
    """
    class Meta:
        model = Review

def manage_reviews(request):
    """Dispatches to the first review.
    """
    reviews = Review.objects.filter()
    
    try:
        review = reviews[0]
        url = reverse("lfs_manage_review", kwargs={"review_id" : review.id })
    except IndexError:
        url = reverse("lfs_add_review")
    
    return HttpResponseRedirect(url)
    
def manage_review(request, review_id=None, template_name="manage/reviews/manage_reviews.html"):
    """The main view to manage a review.
    """
    if review_id is not None:
        review = get_object_or_404(Review, pk=review_id)
        
    reviews = Review.objects.filter()
    
    if request.method == "POST":
        form = ReviewForm(instance=review, data=request.POST)
        if form.is_valid():
            review = form.save()
    else:    
        form = ReviewForm(instance=review)
    
    return render_to_response(template_name, RequestContext(request, {
        "current_review" : review,
        "reviews" : reviews,
        "form" : form,
    }))
    
# Actions
def delete_review(request, review_id):
    """Deletes review with passed review id.
    """
    try:
        review = Review.objects.get(pk=review_id)
    except ObjectDoesNotExist:
        pass
    else:
        review.delete()
        
    return HttpResponseRedirect(reverse("lfs_manage_reviews"))
    
def add_review(request, template_name="manage/reviews/add_review.html"):
    """
    """    
    if request.method == "POST":
        form = ReviewForm(data=request.POST)
        if form.is_valid():
            new_review = form.save()
            return HttpResponseRedirect(reverse("lfs_manage_review", kwargs={"review_id" : new_review.id}))
    else:
        form = ReviewForm()
        
    return render_to_response(template_name, RequestContext(request, {
        "reviews" : Review.objects.all(),
        "form" : form,
    }))