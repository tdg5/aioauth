"""
.. code-block:: python

    from aioauth.oidc.core import grant_type

Different OAuth 2.0 grant types with OpenID Connect extensions.

----
"""
from aioauth.grant_type import (
    AuthorizationCodeGrantType as OAuth2AuthorizationCodeGrantType,
    PasswordGrantType as OAuth2PasswordGrantType,
)
from aioauth.models import Client
from aioauth.oidc.core.responses import TokenResponse
from aioauth.oidc.core.requests import TRequest
from aioauth.storage import TStorage
from aioauth.utils import generate_token


class AuthorizationCodeGrantType(OAuth2AuthorizationCodeGrantType[TRequest, TStorage]):
    """
    The Authorization Code grant type is used by confidential and public
    clients to exchange an authorization code for an access token. After
    the user returns to the client via the redirect URL, the application
    will get the authorization code from the URL and use it to request
    an access token.
    It is recommended that all clients use `RFC 7636 <https://tools.ietf.org/html/rfc7636>`_
    Proof Key for Code Exchange extension with this flow as well to
    provide better security.

    Note:
        Note that ``aioauth`` implements RFC 7636 out-of-the-box.
        See `RFC 6749 section 1.3.1 <https://tools.ietf.org/html/rfc6749#section-1.3.1>`_.
    """

    async def create_token_response(
        self, request: TRequest, client: Client
    ) -> TokenResponse:
        """
        Creates token response to reply to client.

        Extends the OAuth2 authorization_code grant type such that an id_token
        is always included with the access_token.
        """
        if self.scope is None:
            raise RuntimeError("validate_request() must be called first")

        token = await self.storage.create_token(
            request,
            client.client_id,
            self.scope,
            generate_token(42),
            generate_token(48),
        )

        # validate_request will have already ensured the request includes a code.
        assert request.post.code is not None

        authorization_code = await self.storage.get_authorization_code(
            request=request,
            client_id=client.client_id,
            code=request.post.code,
        )

        # validate_request will have already ensured the code was valid.
        assert authorization_code is not None

        id_token = await self.storage.get_id_token(
            client_id=client.client_id,
            nonce=authorization_code.nonce,
            redirect_uri=request.query.redirect_uri,
            request=request,
            response_type="code",
            scope=self.scope,
        )

        await self.storage.delete_authorization_code(
            request,
            client.client_id,
            request.post.code,
        )

        return TokenResponse(
            access_token=token.access_token,
            expires_in=token.expires_in,
            id_token=id_token,
            refresh_token=token.refresh_token,
            refresh_token_expires_in=token.refresh_token_expires_in,
            scope=token.scope,
            token_type=token.token_type,
        )


class PasswordGrantType(OAuth2PasswordGrantType[TRequest, TStorage]):
    """
    The Password grant type is a way to exchange a user's credentials
    for an access token. Because the client application has to collect
    the user's password and send it to the authorization server, it is
    not recommended that this grant be used at all anymore.
    See `RFC 6749 section 1.3.3 <https://tools.ietf.org/html/rfc6749#section-1.3.3>`_.
    The latest `OAuth 2.0 Security Best Current Practice <https://tools.ietf.org/html/draft-ietf-oauth-security-topics-13#section-3.4>`_
    disallows the password grant entirely.
    """

    async def create_token_response(
        self, request: TRequest, client: Client
    ) -> TokenResponse:
        """Creates token response to reply to client."""
        if self.scope is None:
            raise RuntimeError("validate_request() must be called first")

        token = await self.storage.create_token(
            request,
            client.client_id,
            self.scope,
            generate_token(42),
            generate_token(48),
        )

        id_token = await self.storage.get_id_token(
            client_id=client.client_id,
            nonce=None,
            redirect_uri=request.query.redirect_uri,
            request=request,
            response_type="code",
            scope=self.scope,
        )

        return TokenResponse(
            access_token=token.access_token,
            expires_in=token.expires_in,
            id_token=id_token,
            refresh_token=token.refresh_token,
            refresh_token_expires_in=token.refresh_token_expires_in,
            scope=token.scope,
            token_type=token.token_type,
        )
