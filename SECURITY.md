# Política de Segurança — Aurora Restaurante

## Escopo

Este projeto é um sistema educacional de gestão de restaurante criado para estudar APIs, banco de dados, aplicações mobile e comunicação em tempo real.

## Uso

Não use este repositório como sistema de produção sem revisar autenticação, autorização, armazenamento de segredos, exposição de rede, auditoria e configuração de infraestrutura.

## Segredos

Nunca publique:
- `.env`;
- chaves JWT;
- senhas;
- tokens;
- credenciais de banco;
- dados reais de clientes ou funcionários.

Use `.env.example` apenas como modelo.

## Vulnerabilidades

Ao encontrar uma falha de segurança, evite publicar credenciais ou dados reais em issues públicas. Descreva a vulnerabilidade de forma responsável ao mantenedor.

## Estado de segurança

O projeto já utiliza hash de senha, JWT e CORS configurável, mas ainda possui áreas em evolução. A autenticação deve ser estendida para as operações protegidas antes de qualquer exposição pública.
