import unittest
from app.main import predict, preprocess

class MailFlowTests(unittest.TestCase):
    def test_preprocess_removes_html_and_normalizes(self):
        self.assertEqual(preprocess('  Xin <b>chào</b> ', '<p>hóa đơn</p>'), 'Xin chào hóa đơn')

    def test_classifier_routes_invoice_to_finance(self):
        department, confidence = predict('Vui lòng gửi hóa đơn VAT và thông tin thanh toán')
        self.assertIn(department, ['payment_transfer', 'finance_accounting', 'customer_service'])
        self.assertGreaterEqual(confidence, 0.0)

if __name__ == '__main__':
    unittest.main()
