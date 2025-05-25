class Class(Base):
    __tablename__ = 'class'
    class_id = Column(Integer, primary_key=True)
    class_name = Column(Text, nullable=False)

class Subclass(Base):
    __tablename__ = 'subclass'
    subclass_id = Column(Integer, primary_key=True)
    subclass_name = Column(Text, nullable=False)

class ClassNote(Base):
    __tablename__ = 'class_note'
    class_note_id = Column(Integer, primary_key=True)
    class_note = Column(Text, nullable=False)

class Faculty(Base):
    __tablename__ = 'faculty'
    faculty_id = Column(Integer, primary_key=True)
    faculty_name = Column(Text, nullable=False)

class SubjectName(Base):
    __tablename__ = 'subject_name'
    subject_name_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)

class Program(Base):
    __tablename__ = 'program'
    program_id = Column(Integer, primary_key=True)
    program_name = Column(Text, nullable=False) 