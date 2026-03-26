import { API_BASE } from "./api";

const WS_BASE = API_BASE.replace("http://", "ws://").replace("https://", "wss://");

export function criarConexaoWebSocket(canal, { onOpen, onMessage, onClose, onError } = {}) {
  const socket = new WebSocket(`${WS_BASE}/ws/${canal}`);

  socket.onopen = (event) => {
    if (onOpen) onOpen(event);
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (onMessage) onMessage(data);
    } catch (error) {
      console.error("Erro ao interpretar mensagem WebSocket:", error);
    }
  };

  socket.onclose = (event) => {
    if (onClose) onClose(event);
  };

  socket.onerror = (error) => {
    if (onError) onError(error);
  };

  return socket;
}

export function conectarMesas(callbacks = {}) {
  return criarConexaoWebSocket("mesas", callbacks);
}

export function conectarCozinha(callbacks = {}) {
  return criarConexaoWebSocket("cozinha", callbacks);
}

export function conectarBar(callbacks = {}) {
  return criarConexaoWebSocket("bar", callbacks);
}

export function conectarNotificacoes(callbacks = {}) {
  return criarConexaoWebSocket("notificacoes", callbacks);
}

export function conectarCaixa(callbacks = {}) {
  return criarConexaoWebSocket("caixa", callbacks);
}

export function conectarGerencia(callbacks = {}) {
  return criarConexaoWebSocket("gerencia", callbacks);
}

export function fecharConexao(socket) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.close();
  }
}