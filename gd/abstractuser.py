from typing import Sequence, Union

from .abstractentity import AbstractEntity
from .session import _session

from .utils.enums import CommentStrategy, value_to_enum
from .utils.filters import Filters
from .utils.wrap_tools import make_repr, check

class AbstractUser(AbstractEntity):
    """Class that represents an Abstract Geometry Dash User.
    This class is derived from :class:`.AbstractEntity`.
    """
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options
    
    def __repr__(self):
        info = {
            'name': repr(self.name),
            'id': self.id,
            'account_id': self.account_id
        }
        return make_repr(self, info)

    @property
    def name(self):
        """:class:`str`: String representing name of the user."""
        return self.options.get('name')
    
    @property
    def account_id(self):
        """:class:`int`: Account ID of the user."""
        return self.options.get('account_id')

    @property
    def _dict_for_parse(self):
        return {
            k: getattr(self, k) for k in ('name', 'id', 'account_id')
        }

    def as_user(self):
        """Returns `.AbstractUser` object.

        This is used mainly in subclasses.

        Returns
        -------
        :class:`.AbstractUser`
            Abstract User from given object.
        """
        return _session.to_user(self._dict_for_parse, client=self._client)

    async def to_user(self):
        """|coro|

        Convert ``self`` to :class:`.User` object.

        Returns
        -------
        :class:`.User`
            A user object corresponding to the abstract one.
        """
        return await _session.get_user(self.account_id, client=self._client)

    async def send(self, subject: str, body: str, *, from_client=None):
        """|coro|

        Send the message to ``self``. Requires logged client.

        Parameters
        ----------
        subject: :class:`str`
            The subject of the message.

        body: :class:`str`
            The body of the message.

        from_client: :class:`.Client`
            A logged in client to send a message from. If ``None``,
            defaults to a client attached to this user.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to send a message.
        """
        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'send')
        await _session.send_message(target=self, subject=subject, body=body, client=client)

    async def block(self, *, from_client=None):
        """|coro|

        Block a user. Requires logged in client.

        Parameters
        ----------
        from_client: :class:`.Client`
            A logged in client to block a user from. If ``None``,
            defaults to a client attached to this user.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to block a user.
        """
        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'block')
        await _session.block_user(self, unblock=False, client=client)


    async def unblock(self, *, from_client=None):
        """|coro|

        Unblock a user. Requires logged in client.

        Parameters
        ----------
        from_client: :class:`.Client`
            A logged in client to unblock a user from. If ``None``,
            defaults to a client attached to this user.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to unblock a user.
        """
        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'unblock')
        await _session.block_user(self, unblock=True, client=client)

    async def send_friend_request(self, message: str = None, *, from_client=None):
        """|coro|

        Send a friend request to a user.

        .. note::

            This function does not raise any error if request was already sent.

        Parameters
        ----------
        message: :class:`str`
            A message to attach to a request.

        from_client: :class:`.Client`
            A logged in client to send request from. If ``None``,
            defaults to a client attached to this user.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to send a friend request to user.
        """
        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'send_friend_request')
        await _session.send_friend_request(target=self, message=message, client=client)

    async def get_levels_on_page(self, page: int = 0, *, raise_errors: bool = True):
        """|coro|

        Fetches user's levels on a given page.

        This function is equivalent to calling:

        .. code-block:: python3

            await self._client.search_levels_on_page(
                page=page, filters=gd.Filters.setup_by_user(),
                user=self, raise_errors=raise_errors
            )
            # 'self' is an AbstractUser instance here.

        Parameters
        ----------
        page: :class:`int`
            Page to look for levels at.

        raise_errors: :class:`bool`
            Whether to raise errors if nothing was found or fetching failed.

        Returns
        -------
        List[:class:`.Level`]
            All levels found. Can be an empty list.
        """
        filters = Filters.setup_by_user()
        return await self._client.search_levels_on_page(
            page=page, filters=filters, user=self, raise_errors=raise_errors)

    async def get_levels(
        self, pages: Sequence[int] = None,
        *, sort_by_page: bool = True,
        timeout: Union[int, float] = 10.0
    ):
        """|coro|

        Gets levels on specified pages.

        This is equivalent to calling:

        .. code-block:: python3

            return await self._client.search_levels(
                pages=pages, filters=gd.Filters.setup_by_user(),
                user=self, sort_by_page=sort_by_page, timeout=timeout
            )
            # where 'self' is an AbstractUser instance.

        Parameters
        ----------
        pages: Sequence[:class:`int`]
            Pages to look at, represented as a finite sequence, so iterations can be performed.

        sort_by_page: :class:`bool`
            Indicates whether returned levels should be sorted by page.

        timeout: Union[:class:`int`, :class:`float`]
            Timeout to stop requesting after it occurs.
            Used to prevent insanely long responses.

        Returns
        -------
        List[:class:`.Level`]
            List of levels found. Can be an empty list.
        """
        filters = Filters.setup_by_user()
        return await self._client.search_levels(
            pages=pages, filters=filters, user=self, sort_by_page=sort_by_page, timeout=timeout)

    async def get_page_comments(self, page: int = 0):
        """|coro|

        Gets user's profile comments on a specific page.

        This is equivalent to:

        .. code-block:: python3

            await self.retrieve_page_comments('profile', page)
        """
        return await self.retrieve_page_comments('profile', page)

    async def get_page_comment_history(self,
        strategy: Union[int, str, CommentStrategy] = 0, page: int = 0):
        """|coro|

        Retrieves user's level comments. (history)

        Equivalent to calling:

        .. code-block:: python3

            await self.retrieve_page_comments('profile', page, strategy=strategy)
        """
        return await self.retrieve_page_comments('level', page, strategy=strategy)

    async def get_comments(
        self, pages: Sequence[int] = None,
        *, sort_by_page: bool = True,
        timeout: Union[int, float] = 10.0
    ):
        """|coro|

        Gets user's profile comments on specific pages.

        This is equivalent to the following:

        .. code-block:: python3

            await self.retrieve_comments(
                'profile', pages, sort_by_page=sort_by_page, timeout=timeout
            )
        """
        if pages is None:
            pages = range(10)

        return await self.retrieve_comments(
            'profile', pages, sort_by_page=sort_by_page, timeout=timeout
        )

    async def get_comment_history(
        self, strategy: Union[int, str, CommentStrategy] = 0, pages: Sequence[int] = None,
        *, sort_by_page: bool = True, timeout: Union[int, float] = 10.0
    ):
        """|coro|

        Gets user's level (history) comments on specific pages.

        This is equivalent to the following:

        .. code-block:: python3

            await self.retrieve_comments(
                'level', pages, sort_by_page=sort_by_page, timeout=timeout, strategy=strategy
            )
        """
        if pages is None:
            pages = range(10)

        return await self.retrieve_comments(
            'level', pages, sort_by_page=sort_by_page, timeout=timeout, strategy=strategy
        )

    async def retrieve_page_comments(
        self, type: str = 'profile', page: int = 0, *, raise_errors: bool = True,
        strategy: Union[int, str, CommentStrategy] = 0
    ):
        """|coro|

        Utilizes getting comments. This is used in two other methods,
        :meth:`.User.get_page_comments` and :meth:`.User.get_page_comment_history`.

        Parameters
        ----------
        type: :class:`str`
            Type of comments to retrieve. Either `'profile'` or `'level'`.
            Defaults to `'profile'`.

        page: :class:`int`
            Page to look comments at.

        raise_errors: :class:`bool`
            Indicates whether :exc:`.NothingFound` should be raised.
            Should be set to false when getting several pages of comments,
            like in :meth:`.User.retrieve_comments`.

        strategy: Union[:class:`int`, :class:`str`, :class:`.CommentStrategy`]
            A strategy to apply when searching. This is converted to :class:`.CommentStrategy`
            using :func:`.utils.value_to_enum`.

        Returns
        -------
        List[:class:`.Comment`]
            List of all comments retrieved, if comments were found.

        Raises
        ------
        :exc:`.NothingFound`
            No comments were found.
        """
        strategy = value_to_enum(CommentStrategy, strategy)
        return await _session.retrieve_page_comments(
            type=type, user=self, page=page, raise_errors=raise_errors, strategy=strategy
        )

    async def retrieve_comments(
        self, type: str = 'profile', pages: Sequence[int] = None,
        *, sort_by_page: bool = True, timeout: Union[int, float] = 10.0,
        strategy: Union[int, str, CommentStrategy] = 0
    ):
        """|coro|

        Utilizes getting comments on specified pages.

        Parameters
        ----------
        type: :class:`str`
            Type of comments to retrieve. Either `'profile'` or `'level'`.
            Defaults to `'profile'`.

        pages: Sequence[:class:`int`]
            Pages to look at, represented as a finite sequence, so iterations can be performed.

        sort_by_page: :class:`bool`
            Indicates whether returned comments should be sorted by page.

        timeout: Union[:class:`int`, :class:`float`]
            Timeout to stop requesting after it occurs.
            Used to prevent insanely long responses.

        strategy: Union[:class:`int`, :class:`str`, :class:`.CommentStrategy`]
            A strategy to apply when searching. This is converted to :class:`.CommentStrategy`
            using :func:`.utils.value_to_enum`.

        Returns
        -------
        List[:class:`.Comment`]
            List of comments found. Can be an empty list.
        """
        if pages is None:
            pages = range(10)

        strategy = value_to_enum(CommentStrategy, strategy)

        return await _session.retrieve_comments(
            type=type, user=self, pages=pages, sort_by_page=sort_by_page,
            timeout=timeout, strategy=strategy
        )
