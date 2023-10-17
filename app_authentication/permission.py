from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from models import Cadastro

# Criar um grupo para os colaboradores
colaboradores_group, created = Group.objects.get_or_create(name='Colaboradores')

# Adicionar permissões específicas ao grupo (por exemplo, acesso às páginas dos colaboradores)
# Certifique-se de que essas permissões correspondam às páginas ou recursos que os colaboradores podem acessar.
# Você pode criar permissões personalizadas, se necessário.
content_type = ContentType.objects.get_for_model(Cadastro)
permission = Permission.objects.create(
    codename='can_access_colaborador_pages',
    name='Can Access Colaborador Pages',
    content_type=content_type,
)
colaboradores_group.permissions.add(permission)