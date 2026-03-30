"""
Unit tests for Orin.LAB On-chain Agent.
"""

import pytest
from unittest.mock import patch, MagicMock
from agents.onchain_agent import get_balance, get_recent_transactions, rpc_call


class TestRpcCall:
    @patch("agents.onchain_agent.httpx.post")
    def test_returns_result(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"jsonrpc": "2.0", "result": {"value": 5000000000}}
        mock_post.return_value = mock_resp
        result = rpc_call("getBalance", ["some_address"])
        assert result == {"value": 5000000000}

    @patch("agents.onchain_agent.httpx.post")
    def test_returns_empty_on_error(self, mock_post):
        mock_post.side_effect = Exception("Connection refused")
        result = rpc_call("getBalance", ["some_address"])
        assert "error" in result


class TestGetBalance:
    @patch("agents.onchain_agent.rpc_call")
    def test_converts_lamports_to_sol(self, mock_rpc):
        mock_rpc.return_value = {"value": 2_000_000_000}
        balance = get_balance("some_address")
        assert balance == 2.0

    @patch("agents.onchain_agent.rpc_call")
    def test_returns_zero_on_bad_response(self, mock_rpc):
        mock_rpc.return_value = {}
        balance = get_balance("some_address")
        assert balance == 0.0


class TestGetRecentTransactions:
    @patch("agents.onchain_agent.rpc_call")
    def test_returns_list(self, mock_rpc):
        mock_rpc.return_value = [
            {"signature": "abc123", "slot": 100, "err": None},
        ]
        txs = get_recent_transactions("some_address")
        assert isinstance(txs, list)
        assert len(txs) == 1

    @patch("agents.onchain_agent.rpc_call")
    def test_returns_empty_on_bad_response(self, mock_rpc):
        mock_rpc.return_value = {}
        txs = get_recent_transactions("some_address")
        assert txs == []
