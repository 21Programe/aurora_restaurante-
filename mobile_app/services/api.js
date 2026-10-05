const API_BASE =
  process.env.EXPO_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Erro na comunicação com a API");
  }

  return data;
}

export async function login(email, senha) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, senha }),
  });

  return handleResponse(response);
}

export async function listarMesas(status = null) {
  let url = `${API_BASE}/mesas`;

  if (status) {
    url += `?status=${encodeURIComponent(status)}`;
  }

  return handleResponse(await fetch(url));
}

export async function criarMesa(numero, capacidade = 4) {
  return handleResponse(
    await fetch(
      `${API_BASE}/mesas/?numero=${numero}&capacidade=${capacidade}`,
      { method: "POST" }
    )
  );
}

export async function listarProdutos(categoria = null, ativo = null) {
  const params = new URLSearchParams();

  if (categoria) params.append("categoria", categoria);
  if (ativo) params.append("ativo", ativo);

  const query = params.toString();
  const url = `${API_BASE}/produtos/${query ? `?${query}` : ""}`;
  return handleResponse(await fetch(url));
}

export async function criarProduto(nome, categoria, preco) {
  return handleResponse(
    await fetch(
      `${API_BASE}/produtos/?nome=${encodeURIComponent(
        nome
      )}&categoria=${encodeURIComponent(categoria)}&preco=${preco}`,
      { method: "POST" }
    )
  );
}

export async function abrirComanda(mesaId, garcomId) {
  return handleResponse(
    await fetch(
      `${API_BASE}/comandas/abrir?mesa_id=${mesaId}&garcom_id=${garcomId}`,
      { method: "POST" }
    )
  );
}

export async function listarComandas(status = null) {
  let url = `${API_BASE}/comandas`;
  if (status) url += `?status=${encodeURIComponent(status)}`;
  return handleResponse(await fetch(url));
}

export async function adicionarItemComanda(
  comandaId,
  produtoId,
  quantidade = 1,
  observacao = ""
) {
  return handleResponse(
    await fetch(
      `${API_BASE}/comandas/adicionar-item?comanda_id=${comandaId}&produto_id=${produtoId}&quantidade=${quantidade}&observacao=${encodeURIComponent(
        observacao
      )}`,
      { method: "POST" }
    )
  );
}

export async function listarItensComanda(comandaId, status = null) {
  let url = `${API_BASE}/comandas/${comandaId}/itens`;
  if (status) url += `?status=${encodeURIComponent(status)}`;
  return handleResponse(await fetch(url));
}

export async function enviarPedido(comandaId) {
  return handleResponse(
    await fetch(
      `${API_BASE}/comandas/enviar-pedido?comanda_id=${comandaId}`,
      { method: "POST" }
    )
  );
}

export async function listarPedidos(status = null, setor = null) {
  const params = new URLSearchParams();
  if (status) params.append("status", status);
  if (setor) params.append("setor", setor);

  const query = params.toString();
  const url = `${API_BASE}/cozinha/pedidos${query ? `?${query}` : ""}`;
  return handleResponse(await fetch(url));
}

export async function atualizarStatusPedido(pedidoId, novoStatus) {
  return handleResponse(
    await fetch(
      `${API_BASE}/cozinha/pedido/status?pedido_id=${pedidoId}&novo_status=${encodeURIComponent(
        novoStatus
      )}`,
      { method: "POST" }
    )
  );
}

export async function listarNotificacoes() {
  return handleResponse(await fetch(`${API_BASE}/notificacoes/`));
}

export async function resumoComanda(comandaId) {
  return handleResponse(
    await fetch(`${API_BASE}/fechamento/resumo?comanda_id=${comandaId}`)
  );
}

export async function aplicarAjustes(
  comandaId,
  taxaServico = 0,
  desconto = 0
) {
  return handleResponse(
    await fetch(
      `${API_BASE}/fechamento/ajustar?comanda_id=${comandaId}&taxa_servico=${taxaServico}&desconto=${desconto}`,
      { method: "POST" }
    )
  );
}

export async function fecharComanda(
  comandaId,
  formaPagamento = "dinheiro"
) {
  return handleResponse(
    await fetch(
      `${API_BASE}/fechamento/fechar?comanda_id=${comandaId}&forma_pagamento=${encodeURIComponent(
        formaPagamento
      )}`,
      { method: "POST" }
    )
  );
}

export async function cancelarItemComanda(itemId) {
  return handleResponse(
    await fetch(`${API_BASE}/itens-comanda/${itemId}/cancelar`, {
      method: "POST",
    })
  );
}

export async function entregarItemComanda(itemId) {
  return handleResponse(
    await fetch(`${API_BASE}/itens-comanda/${itemId}/entregar`, {
      method: "POST",
    })
  );
}

export { API_BASE };
