import enum
from typing import List, Optional

from core import db
from core.apis.decorators import Principal
from core.libs import helpers, assertions
from core.models.teachers import Teacher
from core.models.students import Student
from sqlalchemy.types import Enum as BaseEnum


class GradeEnum(str, enum.Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'


class AssignmentStateEnum(str, enum.Enum):
    DRAFT = 'DRAFT'
    SUBMITTED = 'SUBMITTED'
    GRADED = 'GRADED'


class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, db.Sequence('assignments_id_seq'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(Teacher.id), nullable=True)
    content = db.Column(db.Text)
    grade = db.Column(BaseEnum(GradeEnum))
    state = db.Column(BaseEnum(AssignmentStateEnum), default=AssignmentStateEnum.DRAFT, nullable=False)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False, onupdate=helpers.get_utc_now)

    def __repr__(self):
        return '<Assignment %r>' % self.id

    @classmethod
    def filter(cls, *criterion):
        db_query = db.session.query(cls)
        return db_query.filter(*criterion)

    @classmethod
    def get_by_id(cls, _id):
        return cls.filter(cls.id == _id).first()

    @classmethod
    def get_by_id_or_404(cls, _id: int) -> Optional['Assignment']:
        """Gets assignment with given id, if assignment is not present raises 404 error"""
        assignment = cls.get_by_id(_id)
        assertions.assert_found(assignment, 'No assignment with this id was found')
        return assignment

    @classmethod
    def upsert(cls, assignment_new: 'Assignment'):
        if assignment_new.id is not None:
            assignment = cls.get_by_id_or_404(assignment_new.id)
            assertions.assert_valid(assignment.state == AssignmentStateEnum.DRAFT,
                                    'only assignment in draft state can be edited')

            assignment.content = assignment_new.content
        else:
            assignment = assignment_new
            db.session.add(assignment_new)

        db.session.flush()
        return assignment

    @classmethod
    def submit(cls, _id, teacher_id, principal: Principal):
        assignment = cls.get_by_id_or_404(_id)
        assertions.assert_valid(assignment.student_id == principal.student_id, 'This assignment belongs to some other student')
        assertions.assert_valid(assignment.content is not None, 'assignment with empty content cannot be submitted')
        assertions.assert_valid(assignment.state != AssignmentStateEnum.SUBMITTED, 'only a draft assignment can be submitted')

        assignment.teacher_id = teacher_id
        assignment.state = AssignmentStateEnum.SUBMITTED
        db.session.flush()

        return assignment

    @classmethod
    def add_grade(cls, _id: int, grade: GradeEnum, principal: Principal) -> 'Assignment':
        """Adds given grade on assignment"""
        assignment = cls.get_by_id_or_404(_id)
        assertions.assert_valid(
            assignment.state == AssignmentStateEnum.SUBMITTED,
            'Only submitted assignment can be graded'
        )
        assertions.assert_valid(
            assignment.teacher_id == principal.teacher_id,
            'This assignment is submitted to some other teacher'
        )

        assignment.grade = grade
        db.session.flush()
        return assignment

    @classmethod
    def get_assignments_by_student(cls, student_id):
        return cls.filter(cls.student_id == student_id).all()

    @classmethod
    def get_assignment_by_teacher(cls, teacher_id: int) -> List["Assignment"]:
        """Retrieves assignments of given teacher_id"""
        return cls.filter(cls.teacher_id == teacher_id).all()
