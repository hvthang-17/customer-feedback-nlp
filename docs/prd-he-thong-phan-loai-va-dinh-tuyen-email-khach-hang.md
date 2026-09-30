# PRD: Hệ thống tự động phân loại và định tuyến email khách hàng bằng NLP

## 1. Tổng quan

Doanh nghiệp thường nhận email khách hàng qua một hộp thư chung. Việc đọc, xác định nội dung và chuyển tiếp thủ công đến đúng phòng ban chậm, dễ nhầm và khó theo dõi. Sản phẩm này là một hệ thống web phục vụ đồ án, cho phép nạp email từ tệp mẫu hoặc API mô phỏng, dùng kỹ thuật xử lý ngôn ngữ tự nhiên (NLP) để dự đoán phòng ban phù hợp, sau đó tự động định tuyến email. Các trường hợp có độ tin cậy thấp hoặc không xác định sẽ được đưa vào hàng đợi kiểm duyệt.

Phạm vi được thiết kế để dễ tạo dữ liệu, dễ trình diễn và không phụ thuộc vào tài khoản Outlook/Gmail thật. Đề tài đồng thời có phần thực nghiệm so sánh các mô hình phân loại văn bản tiếng Việt.

## 2. Mục tiêu

- Tự động phân loại email vào một trong năm phòng ban: Kinh doanh, Chăm sóc khách hàng, Kỹ thuật, Kế toán/Tài chính và Nhân sự.
- Tự động định tuyến email có dự đoán đủ tin cậy đến hàng đợi của phòng ban tương ứng.
- Cho phép quản trị viên kiểm duyệt, sửa nhãn và định tuyến lại các email ngoại lệ.
- Xây dựng dashboard đầy đủ để trình diễn luồng email, kết quả phân loại, hiệu chỉnh và báo cáo.
- So sánh tối thiểu ba mô hình NLP bằng cùng bộ dữ liệu và cùng chỉ số đánh giá.
- Đạt F1-macro tối thiểu 0,80 trên tập kiểm tra nội bộ cho mô hình được chọn để demo (mục tiêu có thể điều chỉnh theo chất lượng dataset).

## 3. Người dùng và vai trò

- **Quản trị viên:** nạp dữ liệu, cấu hình ngưỡng tin cậy, quản lý phòng ban, kiểm duyệt và xem báo cáo.
- **Nhân viên phòng ban:** xem email đã được định tuyến đến phòng ban của mình và cập nhật trạng thái xử lý.
- **Người nghiên cứu/nhóm đồ án:** tạo dataset, huấn luyện mô hình, chạy thực nghiệm và xuất kết quả so sánh.

## 4. User stories

### US-001: Nạp email mẫu
**Description:** Là quản trị viên, tôi muốn tải lên tệp email mẫu hoặc gửi email qua API mô phỏng để hệ thống có dữ liệu phân loại mà không cần kết nối hòm thư thật.

**Acceptance Criteria:**
- [ ] Hệ thống chấp nhận tệp CSV hoặc JSON theo mẫu đã công bố, gồm tối thiểu `subject`, `body`, `sender`, `received_at`.
- [ ] API mô phỏng nhận một email ở định dạng JSON và trả về mã email đã tạo.
- [ ] Mỗi bản ghi lỗi được báo rõ dòng/trường lỗi; các bản ghi hợp lệ vẫn được nạp.
- [ ] Hệ thống lưu email gốc và trạng thái xử lý ban đầu là `new`.
- [ ] Kiểm thử tự động cho xác thực tệp/API đều chạy thành công.

### US-002: Tiền xử lý nội dung email tiếng Việt
**Description:** Là hệ thống, tôi muốn chuẩn hóa tiêu đề và nội dung email để giảm nhiễu trước khi đưa vào mô hình NLP.

**Acceptance Criteria:**
- [ ] Văn bản đầu vào được ghép từ tiêu đề và nội dung, nhưng vẫn lưu riêng hai trường gốc.
- [ ] Pipeline loại bỏ HTML, khoảng trắng dư thừa, chữ ký email phổ biến và nội dung trích dẫn trả lời khi cấu hình bật.
- [ ] Pipeline chuẩn hóa Unicode tiếng Việt và xử lý trường nội dung rỗng.
- [ ] Phiên bản pipeline và cấu hình tiền xử lý được lưu cùng mỗi lần thực nghiệm.
- [ ] Kiểm thử đơn vị bao phủ ít nhất HTML, Unicode và nội dung rỗng.

### US-003: Gán nhãn dữ liệu huấn luyện
**Description:** Là người nghiên cứu, tôi muốn gán hoặc chỉnh sửa nhãn phòng ban cho email để tạo dataset đáng tin cậy.

**Acceptance Criteria:**
- [ ] Có thể gán một trong năm nhãn phòng ban cho từng email.
- [ ] Có thể lọc email chưa gán nhãn và sửa nhãn đã có.
- [ ] Mỗi lần sửa nhãn lưu người sửa, thời điểm sửa và nhãn trước/sau.
- [ ] Có thể xuất dataset đã gán nhãn ở CSV hoặc JSON.
- [ ] Verify in browser using dev-browser skill.

### US-004: Huấn luyện và so sánh mô hình
**Description:** Là người nghiên cứu, tôi muốn chạy thực nghiệm nhiều mô hình trên cùng dataset để chọn mô hình phù hợp nhất.

**Acceptance Criteria:**
- [ ] Hệ thống hỗ trợ tối thiểu ba cấu hình: TF-IDF + Logistic Regression, TF-IDF + SVM và PhoBERT/BERT tiếng Việt fine-tuning.
- [ ] Dữ liệu được chia train/validation/test với seed có thể cấu hình và tránh để cùng email xuất hiện ở nhiều tập.
- [ ] Mỗi lần chạy lưu tên mô hình, siêu tham số, seed, thời gian chạy và phiên bản dataset.
- [ ] Hệ thống tính accuracy, precision, recall, F1-macro, F1 theo từng lớp và confusion matrix trên tập test.
- [ ] Có thể chọn một phiên bản mô hình đã hoàn tất làm mô hình triển khai.
- [ ] Kiểm thử chạy thử nghiệm với dataset nhỏ thành công.

### US-005: Phân loại và tự động định tuyến email
**Description:** Là quản trị viên, tôi muốn email mới được dự đoán phòng ban và tự động chuyển đến đúng hàng đợi để giảm thao tác thủ công.

**Acceptance Criteria:**
- [ ] Khi email mới được nạp, hệ thống trả về nhãn dự đoán, xác suất/độ tin cậy, phiên bản mô hình và thời điểm dự đoán.
- [ ] Email có độ tin cậy lớn hơn hoặc bằng ngưỡng cấu hình được định tuyến tự động đến hàng đợi phòng ban dự đoán.
- [ ] Email dưới ngưỡng hoặc lỗi dự đoán được chuyển đến hàng đợi `Cần kiểm duyệt`, không tự định tuyến.
- [ ] Không tạo bản ghi định tuyến trùng khi gửi lại cùng một yêu cầu có mã idempotency.
- [ ] Nhật ký định tuyến ghi rõ email, nhãn dự đoán, quyết định, thời điểm và phiên bản mô hình.

### US-006: Kiểm duyệt và định tuyến lại ngoại lệ
**Description:** Là quản trị viên, tôi muốn xem và sửa các dự đoán không chắc chắn để email vẫn đến đúng phòng ban.

**Acceptance Criteria:**
- [ ] Dashboard hiển thị danh sách email cần kiểm duyệt, sắp xếp độ tin cậy tăng dần.
- [ ] Quản trị viên có thể chấp nhận dự đoán hoặc chọn phòng ban khác và nhập lý do tùy chọn.
- [ ] Khi sửa, email được chuyển sang hàng đợi phòng ban mới và trạng thái chuyển thành `reviewed`.
- [ ] Quyết định kiểm duyệt được lưu trong lịch sử và có thể dùng làm dữ liệu gán nhãn cho lần huấn luyện sau.
- [ ] Verify in browser using dev-browser skill.

### US-007: Làm việc với hàng đợi phòng ban
**Description:** Là nhân viên phòng ban, tôi muốn xem các email được giao cho phòng ban của mình và cập nhật tiến độ xử lý.

**Acceptance Criteria:**
- [ ] Nhân viên chỉ xem được hàng đợi của phòng ban được phân quyền.
- [ ] Mỗi email hiển thị tiêu đề, người gửi, thời điểm nhận, nhãn dự đoán, độ tin cậy và trạng thái.
- [ ] Có thể đổi trạng thái `new` → `in_progress` → `resolved` hoặc `closed`.
- [ ] Bộ lọc theo trạng thái, khoảng thời gian và độ tin cậy hoạt động chính xác.
- [ ] Verify in browser using dev-browser skill.

### US-008: Dashboard và báo cáo thực nghiệm
**Description:** Là quản trị viên hoặc người nghiên cứu, tôi muốn xem hiệu quả định tuyến và so sánh mô hình để đánh giá hệ thống.

**Acceptance Criteria:**
- [ ] Dashboard hiển thị tổng email, số định tuyến tự động, số cần kiểm duyệt, tỷ lệ được hiệu chỉnh và phân bố theo phòng ban.
- [ ] Trang thực nghiệm hiển thị bảng so sánh chỉ số của các lần chạy mô hình.
- [ ] Có biểu đồ confusion matrix cho lần chạy được chọn.
- [ ] Có thể lọc báo cáo theo khoảng thời gian và xuất bảng số liệu CSV.
- [ ] Verify in browser using dev-browser skill.

## 5. Yêu cầu chức năng

- **FR-1:** Hệ thống phải quản lý đúng năm nhãn phòng ban: `sales`, `customer_service`, `technical`, `finance_accounting`, `human_resources`.
- **FR-2:** Hệ thống phải nhận email qua CSV, JSON và API mô phỏng; không yêu cầu kết nối Outlook/Gmail ở bản đầu.
- **FR-3:** Hệ thống phải lưu nội dung email gốc, nội dung sau tiền xử lý, nguồn nạp, thời điểm nhận và trạng thái.
- **FR-4:** Hệ thống phải hỗ trợ gán nhãn thủ công, sửa nhãn và lưu lịch sử thay đổi nhãn.
- **FR-5:** Hệ thống phải hỗ trợ chạy và lưu kết quả tối thiểu ba mô hình được nêu trong US-004.
- **FR-6:** Mỗi dự đoán phải gồm nhãn, điểm tin cậy, mô hình/phiên bản mô hình và thời gian dự đoán.
- **FR-7:** Quản trị viên phải cấu hình được ngưỡng tự động định tuyến; giá trị mặc định là 0,80.
- **FR-8:** Email có điểm tin cậy dưới ngưỡng phải vào hàng đợi kiểm duyệt; email đạt ngưỡng phải vào hàng đợi phòng ban tương ứng.
- **FR-9:** Hệ thống phải cho phép quản trị viên chấp nhận, sửa và định tuyến lại quyết định phân loại.
- **FR-10:** Hệ thống phải phân quyền tối thiểu theo ba vai trò đã nêu; nhân viên không được xem email của phòng ban khác.
- **FR-11:** Dashboard phải có số liệu vận hành và trang thực nghiệm có bảng chỉ số cùng confusion matrix.
- **FR-12:** Hệ thống phải cung cấp API để nạp email, lấy kết quả dự đoán, xem hàng đợi và cập nhật trạng thái.
- **FR-13:** Hệ thống phải ghi audit log cho nạp email, dự đoán, định tuyến, thay đổi nhãn và thay đổi trạng thái.

## 6. Phi chức năng và kỹ thuật

- Giao diện và dữ liệu hiển thị tiếng Việt, mã hóa UTF-8.
- API nạp/dự đoán một email phải phản hồi dưới 3 giây ở tải demo (không tính thời gian huấn luyện mô hình).
- Huấn luyện mô hình chạy nền hoặc từ tác vụ quản trị; giao diện hiển thị trạng thái chạy và lỗi nếu có.
- Dataset phải được version hóa; kết quả thực nghiệm phải tái lập được bằng seed, cấu hình và phiên bản dữ liệu đã lưu.
- Thông tin định danh nhạy cảm trong dữ liệu demo phải được ẩn danh hóa; không đưa email khách hàng thật vào kho mã nguồn.
- Hệ thống cần cơ chế xác thực, phân quyền và audit log tối thiểu phù hợp cho bản demo.
- Kiến trúc đề xuất: frontend dashboard, backend REST API, cơ sở dữ liệu quan hệ, kho tệp dataset/mô hình và mô-đun NLP tách biệt.

## 7. Cân nhắc thiết kế

- Màn hình tổng quan ưu tiên hiển thị số email mới, tỷ lệ tự động định tuyến, email cần kiểm duyệt và phân bố phòng ban.
- Màu trạng thái phải có nhãn văn bản đi kèm, không chỉ dựa vào màu sắc.
- Trang chi tiết email phải luôn hiển thị nội dung gốc, kết quả dự đoán, lịch sử định tuyến và thao tác kiểm duyệt.
- Kết quả so sánh mô hình cần ghi rõ dataset, cách chia dữ liệu và thông số chạy để có giá trị học thuật.

## 8. Ngoài phạm vi

- Kết nối trực tiếp Outlook, Exchange, Gmail hoặc Google Workspace.
- Tự động gửi email phản hồi cho khách hàng.
- Phân loại đa nhãn (một email thuộc nhiều phòng ban) trong bản đầu.
- Nhận diện cảm xúc, tóm tắt email hoặc chatbot trả lời email.
- Hệ thống SLA, thông báo thời gian thực và tích hợp CRM/ERP.
- Triển khai production quy mô lớn hoặc cam kết độ chính xác cho dữ liệu doanh nghiệp thực.

## 9. Chỉ số thành công

- F1-macro của mô hình được chọn đạt tối thiểu 0,80 trên tập test nội bộ.
- Tỷ lệ email được tự động định tuyến đạt ít nhất 70% với ngưỡng 0,80, đồng thời duy trì precision định tuyến tự động từ 90% trở lên.
- 100% email dưới ngưỡng hoặc lỗi mô hình xuất hiện trong hàng đợi kiểm duyệt.
- Quản trị viên hoàn tất thao tác chấp nhận hoặc sửa một email trong không quá 3 thao tác từ danh sách kiểm duyệt.
- Báo cáo thể hiện được kết quả của ít nhất ba mô hình với các chỉ số và confusion matrix có thể xuất ra.

## 10. Dữ liệu và ví dụ phân loại

| Phòng ban | Ví dụ nội dung email |
| --- | --- |
| Kinh doanh | “Tôi muốn nhận báo giá cho gói dịch vụ doanh nghiệp.” |
| Chăm sóc khách hàng | “Tôi chưa nhận được đơn hàng, vui lòng kiểm tra.” |
| Kỹ thuật | “Tôi không đăng nhập được vào hệ thống từ sáng nay.” |
| Kế toán/Tài chính | “Cho tôi xin hóa đơn VAT của đơn hàng #123.” |
| Nhân sự | “Công ty hiện còn vị trí thực tập sinh không?” |

Dataset nên có tối thiểu 200 mẫu đã gán nhãn cho mỗi lớp để thực nghiệm ban đầu; cần báo cáo rõ nếu số lượng thực tế thấp hơn hoặc mất cân bằng.

## 11. Câu hỏi mở

- Ngưỡng 0,80 có cần cấu hình riêng cho từng phòng ban sau khi có kết quả thực nghiệm không?
- Dataset sẽ được tạo hoàn toàn thủ công, tổng hợp từ nguồn công khai đã ẩn danh, hay kết hợp cả hai?
- Bản demo cần triển khai bằng công nghệ nào (ví dụ: FastAPI/Flask, React, PostgreSQL) để phù hợp năng lực nhóm?
- Có cần cơ chế đăng nhập thật trong demo, hay dùng tài khoản mẫu theo vai trò?
