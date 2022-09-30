from typing import Dict, Any
from app.daos import session_commit
from app.daos.model import Pattern
from app.models.errors import PropertyNotExist


class ModifyPattern:
    _pattern: Pattern
    _data: Dict[str, Any]

    def __init__(self, pattern, data):
        self._data = data
        self._pattern = pattern
        self._handle_dict()
        self._commit()

    def _handle_dict(self):
        for key, val in self._data.items():
            method = getattr(self, f'handle_{key}', None)
            if method is None:
                raise PropertyNotExist(f'{key} 属性不存在')
            method(val)

    def handle_ApiVisibility(self, data):
        self._pattern.ApiVisibility = data

    def handle_ExtensionTyping(self, data):
        self._pattern.ExtensionTyping = data

    def handle_Overload(self, data):
        self._pattern.Overload = data

    def handle_TypeCompatibility(self, data):
        self._pattern.TypingCompatibility = data

    def handle_FunctionalVariable(self, data):
        self._pattern.FunctionalVariable = data

    def handle_BaseclassPresentation(self, data):
        self._pattern.BaseclassPresentation = data

    def handle_MatchedOverload(self, data):
        self._pattern.MatchedOverload = data

    def handle_NewProtocol(self, data):
        self._pattern.NewProtocol = data

    def handle_NewProtocolImplExplicit(self, data):
        self._pattern.NewProtocolImplExplicit = data

    def handle_NewProtocolImplImplicit(self, data):
        self._pattern.NewProtocolImplImplicit = data

    def handle_ExplicitSubClasses(self, data):
        self._pattern.ExplicitSubClasses = data

    def handle_ProtocolUse(self, data):
        self._pattern.ProtocolUse = data

    def handle_ProtocolImplicitImp(self, data):
        self._pattern.ProtocolImplicitImpl = data

    def handle_ProtocolExplicitImpl(self, data):
        self._pattern.ProtocolExplicitImpl = data

    def _commit(self):
        session_commit()


def modify_pattern(pattern, data) -> ModifyPattern.__class__:
    return ModifyPattern(pattern, data)
