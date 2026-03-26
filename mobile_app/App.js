import React, { useEffect, useMemo, useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  FlatList,
  Alert,
  ActivityIndicator,
  SafeAreaView,
} from "react-native";

import {
  listarMesas,
  listarProdutos,
  abrirComanda,
  adicionarItemComanda,
  enviarPedido,
} from "./services/api";

export default function App() {
  const [telaAtual, setTelaAtual] = useState("mesas"); // mesas | cardapio | carrinho
  const [loading, setLoading] = useState(false);
  const [enviandoPedido, setEnviandoPedido] = useState(false);

  const [mesas, setMesas] = useState([]);
  const [produtos, setProdutos] = useState([]);

  const [mesaSelecionada, setMesaSelecionada] = useState(null);
  const [comandaAtualId, setComandaAtualId] = useState(null);

  // carrinho local visual do app
  const [carrinho, setCarrinho] = useState([]);

  useEffect(() => {
    carregarDadosIniciais();
  }, []);

  async function carregarDadosIniciais() {
    setLoading(true);
    try {
      const [mesasData, produtosData] = await Promise.all([
        listarMesas(),
        listarProdutos(null, "sim"),
      ]);

      setMesas(Array.isArray(mesasData) ? mesasData : []);
      setProdutos(Array.isArray(produtosData) ? produtosData : []);
    } catch (error) {
      Alert.alert("Erro", "Não foi possível conectar ao servidor.");
    } finally {
      setLoading(false);
    }
  }

  function resetFluxoMesa() {
    setMesaSelecionada(null);
    setComandaAtualId(null);
    setCarrinho([]);
    setTelaAtual("mesas");
  }

  async function handleSelecionarMesa(mesa) {
    setLoading(true);
    try {
      let idComanda;

      if (mesa.status === "livre") {
        // Fluxo normal: Abre nova comanda para mesa livre (Garçom ID 1 fixo)
        const resposta = await abrirComanda(mesa.id, 1);
        idComanda = resposta.comanda_id;
        setCarrinho([]); // Carrinho visual novo vazio
      } else {
        // Fluxo para mesa ocupada: Busca a comanda que já está aberta
        const comandasAbertas = await listarComandas("aberta");
        const comandaDaMesa = comandasAbertas.find((c) => c.mesa_id === mesa.id);

        if (!comandaDaMesa) {
          throw new Error("Mesa ocupada, mas comanda não encontrada.");
        }

        idComanda = comandaDaMesa.id;
        
        // Opcional: Aqui você pode carregar itensJaPedidos para mostrar o que já tem na mesa
        // const itensJaPedidos = await listarItensComanda(idComanda);
        setCarrinho([]); // Mantemos o carrinho visual limpo para os novos itens desta rodada
      }

      setMesaSelecionada(mesa);
      setComandaAtualId(idComanda);
      setTelaAtual("cardapio");
    } catch (error) {
      Alert.alert("Erro", "Não foi possível acessar a mesa: " + error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleAdicionarProduto(produto) {
    if (!comandaAtualId) {
      Alert.alert("Erro", "Nenhuma comanda ativa encontrada.");
      return;
    }

    try {
      await adicionarItemComanda(comandaAtualId, produto.id, 1, "");

      setCarrinho((estadoAtual) => {
        const indice = estadoAtual.findIndex((item) => item.id === produto.id);

        if (indice >= 0) {
          const atualizado = [...estadoAtual];
          atualizado[indice] = {
            ...atualizado[indice],
            quantidade: atualizado[indice].quantidade + 1,
            subtotal: (atualizado[indice].quantidade + 1) * atualizado[indice].preco,
          };
          return atualizado;
        }

        return [
          ...estadoAtual,
          {
            id: produto.id,
            nome: produto.nome,
            categoria: produto.categoria,
            preco: Number(produto.preco),
            quantidade: 1,
            subtotal: Number(produto.preco),
          },
        ];
      });
    } catch (error) {
      Alert.alert("Erro", "Não foi possível adicionar o item.");
    }
  }

  function aumentarQuantidade(itemId) {
    setCarrinho((estadoAtual) =>
      estadoAtual.map((item) =>
        item.id === itemId
          ? {
              ...item,
              quantidade: item.quantidade + 1,
              subtotal: (item.quantidade + 1) * item.preco,
            }
          : item
      )
    );
  }

  function diminuirQuantidade(itemId) {
    setCarrinho((estadoAtual) =>
      estadoAtual
        .map((item) =>
          item.id === itemId
            ? {
                ...item,
                quantidade: item.quantidade - 1,
                subtotal: (item.quantidade - 1) * item.preco,
              }
            : item
        )
        .filter((item) => item.quantidade > 0)
    );
  }

  const totalCarrinho = useMemo(() => {
    return carrinho.reduce((acc, item) => acc + item.subtotal, 0);
  }, [carrinho]);

  async function handleEnviarPedido() {
    if (!comandaAtualId) {
      Alert.alert("Erro", "Nenhuma comanda ativa encontrada.");
      return;
    }

    if (carrinho.length === 0) {
      Alert.alert("Atenção", "Adicione itens antes de enviar.");
      return;
    }

    setEnviandoPedido(true);
    try {
      // ESTA LINHA É A MAIS IMPORTANTE: 
      // Ela chama o backend para transformar rascunhos em pedidos reais
      await enviarPedido(comandaAtualId); 

      Alert.alert("Enviado!", "A cozinha e o bar já receberam o pedido.");

      // Limpa o estado para o próximo atendimento
      resetFluxoMesa();
      await carregarDadosIniciais(); // Atualiza o status das mesas (ficarão ocupadas)
    } catch (error) {
      Alert.alert("Erro", "Falha ao enviar pedido para o servidor.");
    } finally {
      setEnviandoPedido(false);
    }
  }

  function corMesa(status) {
    switch (status) {
      case "livre":
        return styles.mesaLivre;
      case "ocupada":
      case "pedido_em_preparo":
      case "pronta_para_servir":
      case "aguardando_preparo":
        return styles.mesaOcupada;
      default:
        return styles.mesaPadrao;
    }
  }

  if (loading) {
    return (
      <View style={styles.containerCenter}>
        <ActivityIndicator size="large" color="#38bdf8" />
        <Text style={styles.loadingText}>Carregando...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Aurora Restaurante</Text>
        {telaAtual !== "mesas" && (
          <Text style={styles.headerSubtitle}>Mesa {mesaSelecionada?.numero}</Text>
        )}
      </View>

      {telaAtual === "mesas" && (
        <View style={styles.content}>
          <View style={styles.topRow}>
            <Text style={styles.sectionTitle}>Selecione uma Mesa</Text>
            <TouchableOpacity style={styles.btnMini} onPress={carregarDadosIniciais}>
              <Text style={styles.btnMiniText}>Atualizar</Text>
            </TouchableOpacity>
          </View>

          <FlatList
            data={mesas}
            keyExtractor={(item) => item.id.toString()}
            numColumns={2}
            contentContainerStyle={{ paddingBottom: 20 }}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={[styles.mesaCard, corMesa(item.status)]}
                onPress={() => handleSelecionarMesa(item)}
              >
                <Text style={styles.mesaText}>Mesa {item.numero}</Text>
                <Text style={styles.mesaStatus}>{String(item.status).replaceAll("_", " ")}</Text>
              </TouchableOpacity>
            )}
          />
        </View>
      )}

      {telaAtual === "cardapio" && (
        <View style={styles.content}>
          <View style={styles.menuHeader}>
            <Text style={styles.sectionTitle}>Cardápio</Text>
            <TouchableOpacity style={styles.btnVoltar} onPress={resetFluxoMesa}>
              <Text style={styles.btnVoltarText}>Cancelar</Text>
            </TouchableOpacity>
          </View>

          <FlatList
            data={produtos}
            keyExtractor={(item) => item.id.toString()}
            contentContainerStyle={{ paddingBottom: 100 }}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={styles.produtoCard}
                onPress={() => handleAdicionarProduto(item)}
              >
                <View>
                  <Text style={styles.produtoNome}>{item.nome}</Text>
                  <Text style={styles.produtoCat}>{item.categoria}</Text>
                </View>
                <Text style={styles.produtoPreco}>
                  R$ {Number(item.preco).toFixed(2)}
                </Text>
              </TouchableOpacity>
            )}
          />

          <TouchableOpacity style={styles.btnCarrinho} onPress={() => setTelaAtual("carrinho")}>
            <Text style={styles.btnCarrinhoText}>
              Ver Pedido ({carrinho.reduce((a, i) => a + i.quantidade, 0)} itens)
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {telaAtual === "carrinho" && (
        <View style={styles.content}>
          <View style={styles.menuHeader}>
            <Text style={styles.sectionTitle}>Resumo do Pedido</Text>
            <TouchableOpacity style={styles.btnVoltar} onPress={() => setTelaAtual("cardapio")}>
              <Text style={styles.btnVoltarText}>Voltar</Text>
            </TouchableOpacity>
          </View>

          {carrinho.length === 0 ? (
            <Text style={styles.emptyText}>Nenhum item adicionado.</Text>
          ) : (
            <>
              <FlatList
                data={carrinho}
                keyExtractor={(item) => item.id.toString()}
                contentContainerStyle={{ paddingBottom: 20 }}
                renderItem={({ item }) => (
                  <View style={styles.carrinhoItem}>
                    <View style={{ flex: 1 }}>
                      <Text style={styles.carrinhoNome}>{item.nome}</Text>
                      <Text style={styles.carrinhoPreco}>
                        {item.quantidade}x • R$ {item.preco.toFixed(2)}
                      </Text>
                      <Text style={styles.carrinhoSubtotal}>
                        Subtotal: R$ {item.subtotal.toFixed(2)}
                      </Text>
                    </View>

                    <View style={styles.qtdBox}>
                      <TouchableOpacity
                        style={styles.qtdBtnMenos}
                        onPress={() => diminuirQuantidade(item.id)}
                      >
                        <Text style={styles.qtdBtnText}>-</Text>
                      </TouchableOpacity>

                      <Text style={styles.qtdValor}>{item.quantidade}</Text>

                      <TouchableOpacity
                        style={styles.qtdBtnMais}
                        onPress={() => aumentarQuantidade(item.id)}
                      >
                        <Text style={styles.qtdBtnText}>+</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                )}
              />

              <View style={styles.totalBox}>
                <Text style={styles.totalLabel}>Total do pedido</Text>
                <Text style={styles.totalValue}>R$ {totalCarrinho.toFixed(2)}</Text>
              </View>
            </>
          )}

          <TouchableOpacity
            style={[styles.btnEnviar, enviandoPedido && { opacity: 0.7 }]}
            onPress={handleEnviarPedido}
            disabled={enviandoPedido}
          >
            <Text style={styles.btnEnviarText}>
              {enviandoPedido ? "ENVIANDO..." : "ENVIAR PARA COZINHA"}
            </Text>
          </TouchableOpacity>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0f172a",
  },
  containerCenter: {
    flex: 1,
    backgroundColor: "#0f172a",
    justifyContent: "center",
    alignItems: "center",
  },
  loadingText: {
    color: "#94a3b8",
    marginTop: 10,
    fontSize: 16,
  },

  header: {
    paddingTop: 18,
    paddingBottom: 18,
    paddingHorizontal: 20,
    backgroundColor: "#1e293b",
    borderBottomWidth: 1,
    borderBottomColor: "#334155",
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#f8fafc",
    textAlign: "center",
  },
  headerSubtitle: {
    fontSize: 16,
    color: "#38bdf8",
    textAlign: "center",
    marginTop: 5,
    fontWeight: "bold",
  },

  content: {
    flex: 1,
    padding: 15,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#f8fafc",
    marginBottom: 15,
  },

  topRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  btnMini: {
    backgroundColor: "#38bdf8",
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 10,
  },
  btnMiniText: {
    color: "#0f172a",
    fontWeight: "bold",
  },

  mesaCard: {
    flex: 1,
    margin: 8,
    padding: 20,
    borderRadius: 12,
    alignItems: "center",
  },
  mesaLivre: {
    backgroundColor: "#22c55e",
  },
  mesaOcupada: {
    backgroundColor: "#ef4444",
  },
  mesaPadrao: {
    backgroundColor: "#64748b",
  },
  mesaText: {
    fontSize: 18,
    fontWeight: "bold",
    color: "white",
  },
  mesaStatus: {
    fontSize: 12,
    color: "white",
    marginTop: 5,
    textTransform: "uppercase",
    textAlign: "center",
  },

  menuHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  btnVoltar: {
    padding: 8,
  },
  btnVoltarText: {
    color: "#38bdf8",
    fontWeight: "bold",
  },

  produtoCard: {
    backgroundColor: "#1e293b",
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#334155",
  },
  produtoNome: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#f8fafc",
  },
  produtoCat: {
    fontSize: 12,
    color: "#94a3b8",
    marginTop: 4,
    textTransform: "uppercase",
  },
  produtoPreco: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#38bdf8",
  },

  btnCarrinho: {
    backgroundColor: "#38bdf8",
    padding: 15,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 10,
  },
  btnCarrinhoText: {
    color: "#0f172a",
    fontWeight: "bold",
    fontSize: 16,
  },

  carrinhoItem: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: "#334155",
    gap: 10,
  },
  carrinhoNome: {
    color: "#f8fafc",
    fontSize: 16,
    fontWeight: "bold",
  },
  carrinhoPreco: {
    color: "#94a3b8",
    fontSize: 14,
    marginTop: 4,
  },
  carrinhoSubtotal: {
    color: "#38bdf8",
    fontSize: 14,
    marginTop: 4,
    fontWeight: "bold",
  },
  emptyText: {
    color: "#94a3b8",
    textAlign: "center",
    marginTop: 20,
    fontSize: 16,
  },

  qtdBox: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  qtdBtnMenos: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: "#ef4444",
    justifyContent: "center",
    alignItems: "center",
  },
  qtdBtnMais: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: "#22c55e",
    justifyContent: "center",
    alignItems: "center",
  },
  qtdBtnText: {
    color: "white",
    fontWeight: "bold",
    fontSize: 18,
  },
  qtdValor: {
    color: "#f8fafc",
    minWidth: 24,
    textAlign: "center",
    fontWeight: "bold",
  },

  totalBox: {
    marginTop: 16,
    padding: 16,
    backgroundColor: "#1e293b",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#334155",
  },
  totalLabel: {
    color: "#94a3b8",
    fontSize: 14,
  },
  totalValue: {
    color: "#22c55e",
    fontSize: 24,
    fontWeight: "bold",
    marginTop: 6,
  },

  btnEnviar: {
    backgroundColor: "#22c55e",
    padding: 18,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 20,
  },
  btnEnviarText: {
    color: "white",
    fontWeight: "bold",
    fontSize: 16,
  },
});