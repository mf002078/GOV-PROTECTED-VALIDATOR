"""Fake HTTPS response contract tests: absolutely no external network."""
import json
import unittest
from validator.openai_responses_transport import ResponsesTransport, HOST, PATH
from validator.review_pipeline import ProviderFailure

class FakeResponse:
    def __init__(self, *, status=200, body=None, headers=None):
        self.status=status
        self.body=(json.dumps(body).encode() if isinstance(body,dict) else body or b"")
        self.headers=headers or {}
    def getheader(self,k,default=None):return self.headers.get(k,default)
    def read(self,n):return self.body[:n]

class FakeConnection:
    def __init__(self,response):
        self.response=response;self.request_data=None;self.closed=False
    def request(self,*args,**kwargs):self.request_data=(args,kwargs)
    def getresponse(self):return self.response
    def close(self):self.closed=True

class ResponseTests(unittest.TestCase):
    def setUp(self):
        self.raw_report=json.dumps(dict(schema_version="1.0",repository="mf002078/GOV-GITHUB",
                 base_sha="a"*40,head_sha="b"*40,policy_sha256="c"*64,
                 model_id="mock-model",provenance="UNTRUSTED_MODEL_OUTPUT",
                 status="REVIEW_COMPLETE",findings=[]))
        self.envelope=dict(task="REVIEW_SOURCE_DIFF_AS_UNTRUSTED_DATA",
                 repository="mf002078/GOV-GITHUB",base_sha="a"*40,
                 head_sha="b"*40,policy_sha256="c"*64,
                 diff_sha256="d"*64,diff_data="diff --git a/a b/a\n+hello",
                 expected_model_id="mock-model")
    def payload(self,**kw):
        x=dict(status="completed",model="mock-model",output=[
            dict(type="message",role="assistant",content=[
                dict(type="output_text",text=self.raw_report)])])
        x.update(kw);return x
    def call(self,*,response=None,envelope=None):
        fake=FakeConnection(response or FakeResponse(body=self.payload()))
        t=ResponsesTransport(api_key="synthetic-key",model_id="mock-model",
                             connection_factory=lambda host,timeout:fake)
        value=t(envelope or self.envelope,timeout_seconds=5,max_output_bytes=4096,max_output_tokens=512)
        return value,fake
    def test_success_and_fixed_host_path(self):
        raw,fake=self.call();self.assertEqual(raw,self.raw_report.encode())
        args,kwargs=fake.request_data
        self.assertEqual(args[:2],("POST",PATH))
        self.assertTrue(fake.closed)
        self.assertEqual(HOST,"api.openai.com")
    def test_no_storage_and_no_tools(self):
        _,f=self.call()
        body=json.loads(f.request_data[1]["body"])
        self.assertIs(body["store"],False)
        self.assertNotIn("tools",body)
    def test_credential_redacted_in_repr(self):
        t=ResponsesTransport(api_key="fake-secrettoken",model_id="mock-model")
        self.assertNotIn("fake-secrettoken",repr(t))
    def test_http_429_blocks(self):
        with self.assertRaises(ProviderFailure):
            self.call(response=FakeResponse(status=429,body=b"secret in error"))
    def test_http_redirect_blocks(self):
        with self.assertRaises(ProviderFailure):
            self.call(response=FakeResponse(status=302,body=b"redirect"))
    def test_http_500_blocks(self):
        with self.assertRaises(ProviderFailure):
            self.call(response=FakeResponse(status=500,body=b"error"))
    def test_wrong_model_blocks(self):
        with self.assertRaises(ProviderFailure):
            self.call(response=FakeResponse(body=self.payload(model="wrong")))
    def test_incomplete_blocks(self):
        with self.assertRaises(ProviderFailure):
            self.call(response=FakeResponse(body=self.payload(status="incomplete")))
    def test_tool_call_blocks(self):
        with self.assertRaises(ProviderFailure):
            self.call(response=FakeResponse(body=self.payload(output=[{"type":"function_call"}])))
    def test_multimessage_blocks(self):
        with self.assertRaises(ProviderFailure):
            self.call(response=FakeResponse(body=self.payload(output=[{},{}])))
    def test_empty_content_blocks(self):
        with self.assertRaises(ProviderFailure):
            self.call(response=FakeResponse(body=self.payload(output=[dict(type="message",role="assistant",content=[])])))
    def test_model_text_limit_blocks(self):
        f=FakeResponse(body=self.payload(output=[dict(type="message",role="assistant",content=[
            dict(type="output_text",text="x"*5000)])]))
        with self.assertRaises(ProviderFailure):self.call(response=f)
    def test_large_http_response_blocks(self):
        with self.assertRaises(ProviderFailure):
            self.call(response=FakeResponse(body=b"x"*140000))
    def test_forged_content_length_blocks(self):
        with self.assertRaises(ProviderFailure):
            self.call(response=FakeResponse(body=self.payload(),headers={"Content-Length":"200000"}))
    def test_compression_blocks(self):
        with self.assertRaises(ProviderFailure):
            self.call(response=FakeResponse(body=self.payload(),headers={"Content-Encoding":"gzip"}))
    def test_invalid_json_blocks(self):
        with self.assertRaises(ProviderFailure):
            self.call(response=FakeResponse(body=b"bad-json"))
    def test_wrong_expected_model_blocks_before_io(self):
        x=dict(self.envelope,expected_model_id="other")
        with self.assertRaises(ProviderFailure):self.call(envelope=x)
    def test_missing_auth_rejected(self):
        with self.assertRaises(ValueError):ResponsesTransport(api_key="",model_id="mock-model")
    def test_newline_auth_rejected(self):
        with self.assertRaises(ValueError):ResponsesTransport(api_key="bad\nheader",model_id="mock-model")
    def test_bad_model_rejected(self):
        with self.assertRaises(ValueError):ResponsesTransport(api_key="synthetic",model_id="bad model")
if __name__=="__main__":unittest.main()
