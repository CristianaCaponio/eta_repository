# pylint: disable=useless-super-delegation
# useless-super-delegation for json method. it gives error but it overrides the defaults

"""
Base class for the all the datamodel classes.

Ensure that all the object created by this class are able to serialize themselves into a proper mongodb dictionary
"""
# trick to enable intellisense for pydantic BaseModels
# https://github.com/microsoft/python-language-server/issues/1898
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (TYPE_CHECKING, Any, Callable, Dict, Generator,
                    Optional, Type, TypeVar, Union, NamedTuple)

from bson import ObjectId as BsonObjectId
from bson.objectid import InvalidId
from pydantic import BaseConfig
from pydantic import BaseModel as PydanticBaseModel
from pydantic.v1.typing import is_namedtuple
from pydantic.utils import sequence_like

if TYPE_CHECKING:  # pragma: no cover
    autocomplete = dataclass
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny
else:
    def autocomplete(cls):
        """
        Decorator to trick vscode to show the autocomplete

        Returns
        -------
        Any
            The class decorated by the decorator
        """
        return cls
# -----


# https://github.com/tiangolo/fastapi/issues/1515
# Pydantic doesn't support ObjectID. This is an alternative base model that supports mongo id converting them to string.
# it also implements a

class ObjectId(str):
    """
    Subclass of str. Used to tranform ObjectID objects returned from mongo to strings.
    """
    @classmethod
    def __get_validators__(cls) -> Generator[Callable[[str], BsonObjectId], None, None]:
        """
        Return the validators for this class

        Yields
        -------
        Generator[BsonObjectId, None, None]
            Return the validator used to validate an ObjectID
        """
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> BsonObjectId:
        """
        Check if the given value is a valid ObjectID.

        Parameters
        ----------
        _ : [ObjectId]
            ObjectId class
        value : str
            string representation of an ObjectID

        Returns
        -------
        BsonObjectId
            If `value` is a valid ObjectId

        Raises
        ------
        ValueError
            If `value` is not a valid ObjectId
        """
        try:
            return BsonObjectId(str(value))
        except InvalidId as i:
            raise ValueError(f"{value} is not a valid ObjectId") from i


T = TypeVar('T', bound='BaseModel')  # pylint: disable=invalid-name


class BaseModel(PydanticBaseModel):
    """
    Base class for the all the datamodel classes.

    Ensure that all the object created by this class are able to serialize themselves into a proper mongodb dictionary
    """

    class Config(BaseConfig):
        """
        Default Configuration for the models constructed by subclassing this one
        """
        # pylint: disable=too-few-public-methods
        allow_population_by_field_name = True
        json_encoders = {
            # datetime objects are serialized using the ISO format
            datetime: lambda dt: dt.isoformat(),
            BsonObjectId: str,  # ObjectIDs are serialized as strings
        }

    @classmethod
    def parse_mongo(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Construct an object of the given class by parsing its mongo dictionary representation.

        It is intended to be used when the object is read from a mongo database.

        Parameters
        ----------
        cls : Type[T]
            Actual model class
        data : Dict[str, Any]
            A mongo representation of an object of the class `cls`

        Returns
        -------
        T
            An object of the class `cls` constructed by parsing `data`
        """
        # We must convert _id into "id".
        object_id = data.get('_id', None)
        return cls.parse_obj(dict(data, id=object_id))

    def mongo(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Transform the model into a mongo dictionary

        It is intended to be used when the object needs to be inserted into a mongo database.

        Returns:
            Dict[str, Any]: (MongoDB) Dictionary representation of the model
        """
        exclude_unset = kwargs.pop(
            'exclude_unset', False)  # otherwise will drop the default
        # exclude none by default
        exclude_none = kwargs.pop('exclude_none', True)
        by_alias = kwargs.pop('by_alias', True)  # uses alias unset by default

        parsed = self.dict(
            exclude_unset=exclude_unset,
            exclude_none=exclude_none,
            by_alias=by_alias,
            **kwargs,
        )

        # Mongo uses `_id` as default key. We should stick to that as well.
        if '_id' not in parsed and 'id' in parsed:
            parsed['_id'] = BsonObjectId(
                parsed.pop('id'))  # convert and remove id

        # substitute enum objects with their value
        parsed = self.__enum_to_value(parsed)
        return parsed

    # override default
    def json(
        self,
        *,
        include: Optional[Union['AbstractSetIntStr',
                                'MappingIntStrAny']] = None,
        exclude: Optional[Union['AbstractSetIntStr',
                                'MappingIntStrAny']] = None,
        by_alias: bool = True,  # default by alias
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,  # otherwise will drop the default
        exclude_defaults: bool = False,
        exclude_none: bool = True,  # exclude none by default
        encoder: Optional[Callable[[Any], Any]] = None,
        models_as_dict: bool = True,
        **dumps_kwargs: Any,
    ) -> str:
        return super().json(include=include,
                            exclude=exclude,
                            by_alias=by_alias,
                            skip_defaults=skip_defaults,
                            exclude_unset=exclude_unset,
                            exclude_defaults=exclude_defaults,
                            exclude_none=exclude_none,
                            encoder=encoder,
                            models_as_dict=models_as_dict,
                            **dumps_kwargs)

    def __enum_to_value(self, obj: Any) -> Any:
        """
        Iterates over the given object and substitutes each Enum with its value

        Parameters
        ----------
        obj : Any
            The object to iterate on

        Returns
        -------
        Any
            a copy of the object where the enums have been substituted with their values
        """
        if isinstance(obj, dict):
            return {k_: self.__enum_to_value(v_) for k_, v_ in obj.items()}
        if sequence_like(obj):
            seq_args = (self.__enum_to_value(v_) for v_ in obj)
            return obj.__class__(*seq_args) if is_namedtuple(obj.__class__) else obj.__class__(seq_args)
        if isinstance(obj, Enum):
            return obj.value
        return obj
