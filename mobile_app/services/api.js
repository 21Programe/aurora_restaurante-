const API_BASE =
  process.env.EXPO_PUBLIC_API_URL || "http://127.0.0.1:8000";

let accessToken = null;

export function setAccessToken(token) {
  accessToken = token;
}

export function clearAccessToken() {
  accessToken = null;
}

async function handleResponse(response) {
  const text = await response.text();
  let data = {};

  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: "Resposta inválida do servidor" };
    }
  }

  if (!response.ok) {
    if (response.status === 401) {
      clearAccessToken();
    }
    throw new Error(data.detail || "Erro na comunicação com a API");
  }

  return data;
}

async function apiFetch(url, options = {}) {
  const headers = {
    Accept: "application/json",
    ...(options.headers || {}),
  };

  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  return fetch(url, {...options, headers});
}

export async function login(email, senha) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({email, senha}),
  });

  const data = await handleResponse(response);
  setAccessToken(data.access_token);
  return data;
}

export async function listarMesas(status = null) {
  let url = `${API_BASE}/mesas/`;
  if (status) url += `?status=${encodeURIComponent(status)}`;
  return handleResponse(await apiFetch(url));
}

export async function criarMesa(numero, capacidade = 4) {
  const url = `${API_BASE}/mesas/?numero=${numero}&capacidade=${capacidade}`;
  return handleResponse(await apiFetch(url, {method: "POST"}));
}

export async function listarProdutos(categoria = null, ativo = null) {
  const params = new URLSearchParams();
  if (categoria) params.append("categoria", categoria);
  if (ativo) params.append("ativo", ativo);
  const query = params.toString();
  const url = `${API_BASE}/produtos/${query ? `?${query}` : ""}`;
  return handleResponse(await apiFetch(url));
}

export async function criarProduto(nome, categoria, preco) {
  const url =
    `${API_BASE}/produtos/?nome=${encodeURIComponent(nome)}` +
    `&categoria=${encodeURIComponent(categoria)}&preco=${preco}`;
  return handleResponse(await apiFetch(url, {method: "POST"}));
}

export async function abrirComanda(mesaId) {
  const url = `${API_BASE}/comandas/abrir?mesa_id=${mesaId}`;
  return handleResponse(await apiFetch(url, {method: "POST"}));
}

export async function listarComandas(status = null) {
  let url = `${API_BASE}/comandas/`;
  if (status) {
    url += `?status=${encodeURIComponent(status)}`;
  }
  return handleResponse(await apiFetch(url));
}

export async function adicionarItemComanda(
  comandaId,
  produtoId,
  quantidade = 1,
  observacao = "",
) {
  const url =
    `${API_BASE}/comandas/adicionar-item?comanda_id=${comandaId}` +
    `&produto_id=${produtoId}&quantidade=${quantidade}` +
    `&observacao=${encodeURIComponent(observacao)}`;
  return handleResponse(await apiFetch(url, {method: "POST"}));
}

export async function listarItensComanda(comandaId, status = null) {
  let url = `${API_BASE}/comandas/${comandaId}/itens`;
  if (status) url += `?status=${encodeURIComponent(status)}`;
  return handleResponse(await apiFetch(url));
}

export async function enviarPedido(comandaId) {
  const url = `${API_BASE}/comandas/enviar-pedido?comanda_id=${comandaId}`;
  return handleResponse(await apiFetch(url, {method: "POST"}));
}

export async function listarPedidos(status = null, setor = null) {
  const params = new URLSearchParams();
  if (status) params.append("status", status);
  if (setor) params.append("setor", setor);
  const query = params.toString();
  const url = `${API_BASE}/cozinha/pedidos${query ? `?${query}` : ""}`;
  return handleResponse(await apiFetch(url));
}

export async function atualizarStatusPedido(pedidoId, novoStatus) {
  const url =
    `${API_BASE}/cozinha/pedido/status?pedido_id=${pedidoId}` +
    `&novo_status=${encodeURIComponent(novoStatus)}`;
  return handleResponse(await apiFetch(url, {method: "POST"}));
}

export async function listarNotificacoes() {
  return handleResponse(await apiFetch(`${API_BASE}/notificacoes/`));
}

export async function resumoComanda(comandaId) {
  const url = `${API_BASE}/fechamento/resumo?comanda_id=${comandaId}`;
  return handleResponse(await apiFetch(url));
}

export async function aplicarAjustes(
  comandaId,
  taxaServico = 0,
  desconto = 0,
) {
  const url =
    `${API_BASE}/fechamento/ajustar?comanda_id=${comandaId}` +
    `&taxa_servico=${taxaServico}&desconto=${desconto}`;
  return handleResponse(await apiFetch(url, {method: "POST"}));
}

export async function fecharComanda(
  comandaId,
  formaPagamento = "dinheiro",
) {
  const url =
    `${API_BASE}/fechamento/fechar?comanda_id=${comandaId}` +
    `&forma_pagamento=${encodeURIComponent(formaPagamento)}`;
  return handleResponse(await apiFetch(url, {method: "POST"}));
}

export async function cancelarItemComanda(itemId) {
  const url = `${API_BASE}/itens-comanda/${itemId}/cancelar`;
  return handleResponse(await apiFetch(url, {method: "POST"}));
}

export async function entregarItemComanda(itemId) {
  const url = `${API_BASE}/itens-comanda/${itemId}/entregar`;
  return handleResponse(await apiFetch(url, {method: "POST"}));
}

export {API_BASE};
