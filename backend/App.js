const API_BASE = "http://127.0.0.1:8000";

async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Erro na comunicação com a API");
  }

  return data;
}

export async function login(email, senha) {
  const response = await fetch(
    `${API_BASE}/auth/login?email=${encodeURIComponent(email)}&senha=${encodeURIComponent(senha)}`,
    {
      method: "POST",
    }
  );

  return handleResponse(response);
}

export async function listarMesas(status = null) {
  let url = `${API_BASE}/mesas`;

  if (status) {
    url += `?status=${encodeURIComponent(status)}`;
  }

  const response = await fetch(url);
  return handleResponse(response);
}

export async function criarMesa(numero, capacidade = 4) {
  const response = await fetch(
    `${API_BASE}/mesas/?numero=${numero}&capacidade=${capacidade}`,
    {
      method: "POST",
    }
  );

  return handleResponse(response);
}

export async function listarProdutos(categoria = null, ativo = null) {
  const params = new URLSearchParams();

  if (categoria) params.append("categoria", categoria);
  if (ativo) params.append("ativo", ativo);

  const url = `${API_BASE}/produtos/${params.toString() ? `?${params.toString()}` : ""}`;
  const response = await fetch(url);

  return handleResponse(response);
}

export async function criarProduto(nome, categoria, preco) {
  const response = await fetch(
    `${API_BASE}/produtos/?nome=${encodeURIComponent(nome)}&categoria=${encodeURIComponent(categoria)}&preco=${preco}`,
    {
      method: "POST",
    }
  );

  return handleResponse(response);
}

export async function abrirComanda(mesaId, garcomId) {
  const response = await fetch(
    `${API_BASE}/comandas/abrir?mesa_id=${mesaId}&garcom_id=${garcomId}`,
    {
      method: "POST",
    }
  );

  return handleResponse(response);
}

export async function listarComandas(status = null) {
  let url = `${API_BASE}/comandas`;

  if (status) {
    url += `?status=${encodeURIComponent(status)}`;
  }

  const response = await fetch(url);
  return handleResponse(response);
}

export async function adicionarItemComanda(comandaId, produtoId, quantidade = 1, observacao = "") {
  const response = await fetch(
    `${API_BASE}/comandas/adicionar-item?comanda_id=${comandaId}&produto_id=${produtoId}&quantidade=${quantidade}&observacao=${encodeURIComponent(observacao)}`,
    {
      method: "POST",
    }
  );

  return handleResponse(response);
}

export async function listarItensComanda(comandaId, status = null) {
  let url = `${API_BASE}/comandas/${comandaId}/itens`;

  if (status) {
    url += `?status=${encodeURIComponent(status)}`;
  }

  const response = await fetch(url);
  return handleResponse(response);
}

export async function enviarPedido(comandaId) {
  const response = await fetch(
    `${API_BASE}/comandas/enviar-pedido?comanda_id=${comandaId}`,
    {
      method: "POST",
    }
  );

  return handleResponse(response);
}

export async function listarPedidos(status = null, setor = null) {
  const params = new URLSearchParams();

  if (status) params.append("status", status);
  if (setor) params.append("setor", setor);

  const url = `${API_BASE}/cozinha/pedidos${params.toString() ? `?${params.toString()}` : ""}`;
  const response = await fetch(url);

  return handleResponse(response);
}

export async function atualizarStatusPedido(pedidoId, novoStatus) {
  const response = await fetch(
    `${API_BASE}/cozinha/pedido/status?pedido_id=${pedidoId}&novo_status=${encodeURIComponent(novoStatus)}`,
    {
      method: "POST",
    }
  );

  return handleResponse(response);
}

export async function listarNotificacoes() {
  const response = await fetch(`${API_BASE}/notificacoes/`);
  return handleResponse(response);
}

export async function resumoComanda(comandaId) {
  const response = await fetch(`${API_BASE}/fechamento/resumo?comanda_id=${comandaId}`);
  return handleResponse(response);
}

export async function aplicarAjustes(comandaId, taxaServico = 0, desconto = 0) {
  const response = await fetch(
    `${API_BASE}/fechamento/ajustar?comanda_id=${comandaId}&taxa_servico=${taxaServico}&desconto=${desconto}`,
    {
      method: "POST",
    }
  );

  return handleResponse(response);
}

export async function fecharComanda(comandaId, formaPagamento = "dinheiro") {
  const response = await fetch(
    `${API_BASE}/fechamento/fechar?comanda_id=${comandaId}&forma_pagamento=${encodeURIComponent(formaPagamento)}`,
    {
      method: "POST",
    }
  );

  return handleResponse(response);
}

export async function cancelarItemComanda(itemId) {
  const response = await fetch(`${API_BASE}/itens-comanda/${itemId}/cancelar`, {
    method: "POST",
  });

  return handleResponse(response);
}

export async function entregarItemComanda(itemId) {
  const response = await fetch(`${API_BASE}/itens-comanda/${itemId}/entregar`, {
    method: "POST",
  });

  return handleResponse(response);
}

export { API_BASE };