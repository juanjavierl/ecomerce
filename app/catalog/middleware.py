from django.contrib.auth.models import User

AFFILIATE_SESSION_KEY = "affiliate_user_id"
AFFILIATE_GROUP_NAME = "Afiliados"


class AffiliateReferenceMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Si ya existe un afiliado en la sesión no hacemos nada
        if not request.session.get(AFFILIATE_SESSION_KEY):

            affiliate_user_id = request.GET.get("ref", "").strip()

            if affiliate_user_id.isdigit():

                exists = User.objects.filter(
                    id=int(affiliate_user_id),
                    is_active=True,
                    groups__name=AFFILIATE_GROUP_NAME
                ).exists()

                if exists:
                    request.session[AFFILIATE_SESSION_KEY] = int(affiliate_user_id)

        response = self.get_response(request)

        return response