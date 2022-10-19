import datetime
from app.daos import db


class User(db.Model):
    """
    用户数据模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    nickname = db.Column(db.String, nullable=False, default='新建用户')
    user_type = db.Column(db.Integer, nullable=False, default=2)


class Project(db.Model):
    """
    项目数据模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String, nullable=False)
    encode_name = db.Column(db.String, nullable=False)
    version = db.Column(db.String, nullable=False, default="v1.0.0")
    file = db.Column(db.Integer, nullable=False, default=0)
    loc = db.Column(db.Integer, nullable=False, default=0)
    type_manner = db.Column(db.String, nullable=True, default="inline")
    code_url = db.Column(db.String, nullable=False, default="private")
    star = db.Column(db.String, nullable=False, default="0")
    step = db.Column(db.Integer, nullable=False, default=0)


class Coverage(db.Model):
    """
    项目类型覆盖率模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), name="project_id", nullable=False, primary_key=True)
    loc = db.Column(db.Float, nullable=False, default=0)
    func = db.Column(db.Float, nullable=False, default=0)
    file = db.Column(db.Float, nullable=False, default=0)
    var = db.Column(db.Float, nullable=False, default=0)
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)


class DiverseUsage(db.Model):
    """
    使用统计模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), name="project_id", nullable=False, primary_key=True)
    Optional = db.Column(db.Integer, nullable=False, default=0)
    Any = db.Column(db.Integer, nullable=False, default=0)
    List = db.Column(db.Integer, nullable=False, default=0)
    Union = db.Column(db.Integer, nullable=False, default=0)
    Dict = db.Column(db.Integer, nullable=False, default=0)
    Tuple = db.Column(db.Integer, nullable=False, default=0)
    Type = db.Column(db.Integer, nullable=False, default=0)
    Callable = db.Column(db.Integer, nullable=False, default=0)
    MutableMapping = db.Column(db.Integer, nullable=False, default=0)
    Sequence = db.Column(db.Integer, nullable=False, default=0)
    Iterable = db.Column(db.Integer, nullable=False, default=0)
    Set = db.Column(db.Integer, nullable=False, default=0)
    Mapping = db.Column(db.Integer, nullable=False, default=0)
    Others = db.Column(db.Integer, nullable=False, default=0)
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)


class Pattern(db.Model):
    """
    stub复杂类型使用情况模型
    """
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), name="project_id", nullable=False, primary_key=True)
    ApiVisibility = db.Column(db.Integer, nullable=False, default=0)
    ExtensionTyping = db.Column(db.Integer, nullable=False, default=0)
    MatchedOverload = db.Column(db.Integer, nullable=False, default=0)
    Overload = db.Column(db.Integer, nullable=False, default=0)
    TypingCompatibility = db.Column(db.Integer, nullable=False, default=0)
    FunctionalVariable = db.Column(db.Integer, nullable=False, default=0)
    BaseclassPresentation = db.Column(db.Integer, nullable=False, default=0)
    NewProtocol = db.Column(db.Integer, nullable=False, default=0)
    NewProtocolImplExplicit = db.Column(db.Integer, nullable=False, default=0)
    NewProtocolImplImplicit = db.Column(db.Integer, nullable=False, default=0)
    ExplicitSubClasses = db.Column(db.Integer, nullable=False, default=0)
    ProtocolUse = db.Column(db.Integer, nullable=False, default=0)
    ProtocolImplicitImpl = db.Column(db.Integer, nullable=False, default=0)
    ProtocolExplicitImpl = db.Column(db.Integer, nullable=False, default=0)
    update_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    delete_at = db.Column(db.DateTime, nullable=True)
