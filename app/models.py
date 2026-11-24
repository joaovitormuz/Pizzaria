
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator


# =====================================================
# GERENCIAMENTO DE USUÁRIOS
# =====================================================

class UsuarioManager(BaseUserManager):

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('O nome de usuário é obrigatório.')

        user = self.model(
            username=username,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('O superusuário precisa ter is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('O superusuário precisa ter is_superuser=True.')

        return self.create_user(
            username=username,
            password=password,
            **extra_fields
        )


class Usuario(AbstractUser):

    nome = models.CharField(max_length=100)

    email = models.EmailField(
        blank=True,
        null=True
    )

    numero_telefone = models.CharField(max_length=20)

    endereco = models.CharField(max_length=255)

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    def __str__(self):
        return self.nome


class Cliente(Usuario):

    referencia_pagamento = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    def realizarPedido(self):
        pass

    def consultarPedidos(self):
        pass

    def __str__(self):
        return self.nome


class Funcionario(Usuario):

    salario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    disponibilidade = models.BooleanField(default=True)
    funcao = models.CharField(max_length=100)

    def atualizarStatus(self):
        pass

    def __str__(self):
        return self.nome


class Entregador(Usuario):

    taxa_entrega = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    disponibilidade = models.BooleanField(default=True)

    def realizarEntrega(self):
        pass

    def atualizarStatusEntrega(self):
        pass

    def __str__(self):
        return self.nome


# =====================================================
# GERENCIAMENTO DA PIZZARIA
# =====================================================

class Pizzaria(models.Model):

    id_pizzaria = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    numero_telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=255)
    horario_funcionamento = models.CharField(max_length=100)

    def cadastrar(self):
        pass

    def atualizar(self):
        pass

    def consultar(self):
        pass

    def __str__(self):
        return self.nome


# =====================================================
# GERENCIAMENTO DE INGREDIENTES E ESTOQUE
# =====================================================

class Ingrediente(models.Model):

    id_ingrediente = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    unidade_medida = models.CharField(max_length=30)

    def atualizarIngrediente(self):
        pass

    def __str__(self):
        return self.nome


class Estoque(models.Model):

    id_estoque = models.AutoField(primary_key=True)

    ingrediente = models.OneToOneField(
        Ingrediente,
        on_delete=models.CASCADE,
        related_name='estoque'
    )

    quantidade_estoque = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0)]
    )

    quantidade_minima = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0)]
    )

    data_atualizacao = models.DateTimeField(auto_now=True)

    def atualizarEstoque(self):
        pass

    def verificarEstoque(self):
        return self.quantidade_estoque <= self.quantidade_minima

    def __str__(self):
        return f'Estoque: {self.ingrediente.nome}'


# =====================================================
# GERENCIAMENTO DE PRODUTOS
# =====================================================

class Produto(models.Model):

    id_produto = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    descricao = models.TextField(blank=True)

    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    disponibilidade = models.BooleanField(default=True)

    def atualizarProduto(self):
        pass

    def consultarProduto(self):
        pass

    def __str__(self):
        return self.nome


# =====================================================
# RECEITAS DOS PRODUTOS
# =====================================================

class Receita(models.Model):

    id_receita = models.AutoField(primary_key=True)

    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='receitas'
    )

    ingrediente = models.ForeignKey(
        Ingrediente,
        on_delete=models.CASCADE,
        related_name='receitas'
    )

    unidade_medida = models.CharField(max_length=30)

    quantidade_medida = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['produto', 'ingrediente'],
                name='receita_produto_ingrediente_unico'
            )
        ]

    def atualizarIngrediente(self):
        pass

    def __str__(self):
        return f'{self.produto.nome} - {self.ingrediente.nome}'


# =====================================================
# GERENCIAMENTO DE PEDIDOS
# =====================================================

class Pedido(models.Model):

    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Em preparação', 'Em preparação'),
        ('Pronto', 'Pronto'),
        ('Em entrega', 'Em entrega'),
        ('Concluído', 'Concluído'),
        ('Cancelado', 'Cancelado'),
    ]

    TIPO_ENTREGA_CHOICES = [
        ('Entrega', 'Entrega'),
        ('Retirada', 'Retirada'),
    ]

    id_pedido = models.AutoField(primary_key=True)

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='pedidos'
    )

    data_hora = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Pendente'
    )

    preco_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    tempo_estimado = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Tempo estimado em minutos'
    )

    tipo_entrega = models.CharField(
        max_length=20,
        choices=TIPO_ENTREGA_CHOICES
    )

    endereco_entrega = models.CharField(
        max_length=255,
        blank=True
    )

    def calcularTotal(self):
        total = sum(
            item.subtotal for item in self.itens.all()
        )
        self.preco_total = total
        self.save(update_fields=['preco_total'])
        return total

    def atualizarStatus(self):
        pass

    def cancelarPedido(self):
        self.status = 'Cancelado'
        self.save(update_fields=['status'])

    def __str__(self):
        return f'Pedido #{self.id_pedido}'


# =====================================================
# ITENS DOS PEDIDOS
# =====================================================

class ItemPedido(models.Model):

    id_item = models.AutoField(primary_key=True)

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens'
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='itens_pedido'
    )

    quantidade = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def calcularSubtotal(self):
        self.subtotal = self.quantidade * self.preco_unitario
        self.save(update_fields=['subtotal'])
        return self.subtotal

    def __str__(self):
        return f'{self.produto.nome} - Pedido {self.pedido.id_pedido}'


# =====================================================
# GERENCIAMENTO DE PAGAMENTOS
# =====================================================

class Pagamento(models.Model):

    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Aprovado', 'Aprovado'),
        ('Recusado', 'Recusado'),
        ('Estornado', 'Estornado'),
    ]

    id_pagamento = models.AutoField(primary_key=True)

    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        related_name='pagamento'
    )

    data_pagamento = models.DateTimeField(
        null=True,
        blank=True
    )

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    metodo_pagamento = models.CharField(max_length=50)

    status_pagamento = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pendente'
    )

    def processarPagamento(self):
        pass

    def validarPagamento(self):
        pass

    def __str__(self):
        return f'Pagamento do pedido {self.pedido.id_pedido}'


# =====================================================
# PROCESSAMENTO DOS PEDIDOS
# =====================================================

class ProcessamentoPedido(models.Model):

    STATUS_CHOICES = [
        ('Aguardando', 'Aguardando'),
        ('Em preparação', 'Em preparação'),
        ('Finalizado', 'Finalizado'),
    ]

    id_processamento = models.AutoField(primary_key=True)

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='processamentos'
    )

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        related_name='processamentos'
    )

    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField(null=True, blank=True)

    status_preparacao = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Aguardando'
    )

    observacao = models.TextField(blank=True)

    def atualizarStatus(self):
        pass

    def finalizarPreparo(self):
        pass

    def __str__(self):
        return f'Processamento do pedido {self.pedido.id_pedido}'


# =====================================================
# GERENCIAMENTO DE ENTREGAS
# =====================================================

class Entrega(models.Model):

    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Saiu para entrega', 'Saiu para entrega'),
        ('Entregue', 'Entregue'),
        ('Cancelada', 'Cancelada'),
    ]

    id_entrega = models.AutoField(primary_key=True)

    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        related_name='entrega'
    )

    entregador = models.ForeignKey(
        Entregador,
        on_delete=models.PROTECT,
        related_name='entregas',
        null=True,
        blank=True
    )

    endereco_entrega = models.CharField(max_length=255)

    data_saida = models.DateTimeField(
        null=True,
        blank=True
    )

    data_entrega = models.DateTimeField(
        null=True,
        blank=True
    )

    status_entrega = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Pendente'
    )

    taxa_entrega = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    def atualizarStatus(self):
        pass

    def confirmarEntrega(self):
        pass

    def __str__(self):
        return f'Entrega do pedido {self.pedido.id_pedido}'
