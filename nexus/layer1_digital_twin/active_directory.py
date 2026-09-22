import uuid
import random
from dataclasses import dataclass, field
from typing import List, Optional
from faker import Faker

@dataclass
class ADUser:
    username: str
    first_name: str
    last_name: str
    email: str
    department: str
    role: str
    employee_id: str
    groups: List[str]
    is_service_account: bool
    is_active: bool = True

@dataclass
class ADGroup:
    name: str
    description: str

class ActiveDirectorySimulator:
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        self.faker = Faker()
        self.departments = ['IT', 'Finance', 'HR', 'Engineering', 'Sales', 'Marketing', 'Executive']
        self.groups = [
            ADGroup('Domain Admins', 'Domain Administrators'),
            ADGroup('IT Staff', 'IT Department Users'),
            ADGroup('Finance Users', 'Finance Department Users'),
            ADGroup('HR Users', 'HR Department Users'),
            ADGroup('Engineering Users', 'Engineering Department Users'),
            ADGroup('All Employees', 'All Domain Users')
        ]
        self.users: List[ADUser] = []

    def generate_users(self, count: int) -> List[ADUser]:
        new_users = []
        for _ in range(count):
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            username = f"{first_name[0].lower()}{last_name.lower()}"
            department = random.choice(self.departments)
            
            groups = ['All Employees']
            role = f"{department} Staff"
            
            if department == 'IT':
                groups.append('IT Staff')
                if random.random() < 0.2:
                    groups.append('Domain Admins')
            elif department == 'Finance':
                groups.append('Finance Users')
            elif department == 'HR':
                groups.append('HR Users')
            elif department == 'Engineering':
                groups.append('Engineering Users')
                
            user = ADUser(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=f"{username}@nexuscorp.local",
                department=department,
                role=role,
                employee_id=str(uuid.uuid4()),
                groups=groups,
                is_service_account=False
            )
            new_users.append(user)
        self.users.extend(new_users)
        return new_users

    def generate_service_accounts(self) -> None:
        service_names = [
            ('svc_backup', True),
            ('svc_sql', False),
            ('svc_web', False),
            ('svc_exchange', False),
            ('svc_deploy', True)
        ]
        for name, is_admin in service_names:
            groups = ['All Employees']
            if is_admin:
                groups.append('Domain Admins')
            user = ADUser(
                username=name,
                first_name='Service',
                last_name=name.split('_')[1].capitalize(),
                email=f"{name}@nexuscorp.local",
                department='IT',
                role='Service Account',
                employee_id=str(uuid.uuid4()),
                groups=groups,
                is_service_account=True
            )
            self.users.append(user)

    def get_all_accounts(self) -> List[ADUser]:
        return self.users

    def get_user_by_name(self, username: str) -> Optional[ADUser]:
        for user in self.users:
            if user.username == username:
                return user
        return None

    def disable_account(self, username: str) -> bool:
        user = self.get_user_by_name(username)
        if user:
            user.is_active = False
            return True
        return False
