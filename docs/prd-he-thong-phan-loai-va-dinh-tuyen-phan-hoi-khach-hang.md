# PRD: Xây dựng hệ thống tự động phân loại lĩnh vực, phân tích cảm xúc và định tuyến phản hồi khách hàng trong doanh nghiệp ngân hàng dựa trên kỹ thuật xử lý ngôn ngữ tự nhiên

## 1. Tổng quan

Doanh nghiệp ngân hàng nhận nhiều đánh giá, phản hồi và yêu cầu hỗ trợ của khách hàng trên các kênh công khai. Việc đọc, xác định lĩnh vực, nhận biết cảm xúc và chuyển thủ công đến đơn vị xử lý phù hợp chậm, dễ nhầm và khó theo dõi. Sản phẩm này là hệ thống web phục vụ đồ án, dùng kỹ thuật xử lý ngôn ngữ tự nhiên (NLP) để phân loại lĩnh vực nghiệp vụ, phân tích cảm xúc và định tuyến phản hồi đến hàng đợi xử lý tương ứng. Các trường hợp có độ tin cậy thấp, nhiều lĩnh vực hoặc không ánh xạ rõ sẽ vào hàng đợi kiểm duyệt.

Dataset cốt lõi là **UTS2017_Bank**: 2.471 phản hồi tiếng Việt đã ẩn danh, gán 14 nhãn lĩnh vực ngân hàng và nhãn cảm xúc `positive`, `negative`, `neutral`. Đây là dữ liệu phản hồi/đánh giá, không phải email; hệ thống trong phạm vi này xử lý đánh giá khách hàng và không khẳng định đã đánh giá trên email thực tế. Cả hai tác vụ dùng duy nhất mô hình **TF-IDF + SVM**.

## 2. Mục tiêu

- Tự động phân loại lĩnh vực đánh giá khách hàng vào năm hàng đợi nghiệp vụ: Chăm sóc khách hàng, Thẻ & Tài khoản, Ngân hàng số, Tín dụng & Tiết kiệm, Thanh toán & Chuyển tiền.
- Tự động phân tích cảm xúc phản hồi thành `positive`, `negative` hoặc `neutral`.
- Tự động định tuyến đánh giá có dự đoán đủ tin cậy đến hàng đợi nghiệp vụ tương ứng.
- Cho phép quản trị viên kiểm duyệt, sửa nhãn và định tuyến lại các đánh giá ngoại lệ.
- Xây dựng dashboard đầy đủ để trình diễn luồng đánh giá, kết quả phân loại, hiệu chỉnh và báo cáo.
- Huấn luyện, đánh giá và triển khai TF-IDF + SVM cho cả tác vụ phân loại lĩnh vực và phân tích cảm xúc.
- Đạt F1-macro tối thiểu 0,80 trên tập kiểm tra nội bộ cho từng tác vụ (mục tiêu có thể điều chỉnh theo chất lượng dataset).

## 3. Người dùng và vai trò

- **Quản trị viên:** nạp dữ liệu, cấu hình ngưỡng tin cậy, quản lý hàng đợi nghiệp vụ, kiểm duyệt và xem báo cáo.
- **Nhân viên đơn vị xử lý:** xem đánh giá đã được định tuyến đến hàng đợi của mình và cập nhật trạng thái xử lý.
- **Người nghiên cứu/nhóm đồ án:** tạo dataset, huấn luyện mô hình, chạy thực nghiệm và xuất kết quả so sánh.

## 4. User stories

### US-001: Nạp dataset đánh giá khách hàng
**Description:** Là quản trị viên, tôi muốn nạp dataset UTS2017_Bank và các đánh giá bổ sung đã được chuẩn hóa để hệ thống có dữ liệu phân loại.

**Acceptance Criteria:**
- [ ] Hệ thống chấp nhận tệp CSV hoặc JSON theo mẫu đã công bố, gồm tối thiểu `text`, `label`, `source` và `received_at`.
- [ ] API nhận một đánh giá ở định dạng JSON và trả về mã bản ghi đã tạo.
- [ ] Mỗi bản ghi lỗi được báo rõ dòng/trường lỗi; các bản ghi hợp lệ vẫn được nạp.
- [ ] Hệ thống lưu văn bản đánh giá gốc, nguồn dữ liệu, nhãn gốc (nếu có) và trạng thái xử lý ban đầu là `new`.
- [ ] Kiểm thử tự động cho xác thực tệp/API đều chạy thành công.

### US-002: Tiền xử lý đánh giá tiếng Việt
**Description:** Là hệ thống, tôi muốn chuẩn hóa nội dung đánh giá khách hàng để giảm nhiễu trước khi đưa vào mô hình NLP.

**Acceptance Criteria:**
- [ ] Văn bản đầu vào sử dụng trường `text`; văn bản gốc luôn được lưu riêng, không bị ghi đè.
- [ ] Pipeline loại bỏ HTML, URL, khoảng trắng dư thừa và thông tin định danh còn sót lại khi cấu hình bật.
- [ ] Pipeline chuẩn hóa Unicode tiếng Việt và xử lý trường nội dung rỗng.
- [ ] Phiên bản pipeline và cấu hình tiền xử lý được lưu cùng mỗi lần thực nghiệm.
- [ ] Kiểm thử đơn vị bao phủ ít nhất HTML, Unicode và nội dung rỗng.

### US-003: Gán nhãn dữ liệu huấn luyện
**Description:** Là người nghiên cứu, tôi muốn ánh xạ hoặc chỉnh sửa nhãn đánh giá sang hàng đợi nghiệp vụ để tạo dataset định tuyến đáng tin cậy.

**Acceptance Criteria:**
- [ ] Có thể gán một trong năm nhãn hàng đợi nghiệp vụ cho từng đánh giá.
- [ ] Có thể lọc đánh giá chưa gán nhãn và sửa nhãn đã có.
- [ ] Mỗi lần sửa nhãn lưu người sửa, thời điểm sửa và nhãn trước/sau.
- [ ] Có thể xuất dataset đã gán nhãn ở CSV hoặc JSON.
- [ ] Verify in browser using dev-browser skill.

### US-004: Huấn luyện mô hình phân loại lĩnh vực và cảm xúc
**Description:** Là người nghiên cứu, tôi muốn huấn luyện và đánh giá TF-IDF + SVM cho hai tác vụ để sử dụng kết quả đáng tin cậy khi định tuyến.

**Acceptance Criteria:**
- [ ] Hệ thống chỉ sử dụng một cấu hình mô hình: TF-IDF + SVM.
- [ ] Dữ liệu được chia train/validation/test với seed có thể cấu hình và tránh để cùng đánh giá xuất hiện ở nhiều tập.
- [ ] Mỗi lần chạy lưu tác vụ (`domain_classification` hoặc `sentiment_analysis`), siêu tham số SVM, cấu hình TF-IDF, seed, thời gian chạy và phiên bản dataset.
- [ ] Hệ thống tính accuracy, precision, recall, F1-macro, F1 theo từng lớp và confusion matrix riêng cho mỗi tác vụ trên tập test.
- [ ] Có thể chọn một phiên bản đã hoàn tất cho từng tác vụ để triển khai.
- [ ] Kiểm thử chạy thử nghiệm với dataset nhỏ thành công.

### US-005: Phân loại và tự động định tuyến đánh giá
**Description:** Là quản trị viên, tôi muốn đánh giá mới được dự đoán hàng đợi xử lý và tự động chuyển đến đúng đơn vị để giảm thao tác thủ công.

**Acceptance Criteria:**
- [ ] Khi đánh giá mới được nạp, hệ thống trả về nhãn lĩnh vực, nhãn cảm xúc, độ tin cậy, phiên bản mô hình và thời điểm dự đoán.
- [ ] Đánh giá có độ tin cậy lớn hơn hoặc bằng ngưỡng cấu hình được định tuyến tự động đến hàng đợi dự đoán.
- [ ] Đánh giá dưới ngưỡng, đa chủ đề hoặc lỗi dự đoán được chuyển đến hàng đợi `Cần kiểm duyệt`, không tự định tuyến.
- [ ] Không tạo bản ghi định tuyến trùng khi gửi lại cùng một yêu cầu có mã idempotency.
- [ ] Nhật ký định tuyến ghi rõ đánh giá, nhãn lĩnh vực, nhãn cảm xúc, quyết định, thời điểm và phiên bản mô hình.

### US-006: Kiểm duyệt và định tuyến lại ngoại lệ
**Description:** Là quản trị viên, tôi muốn xem và sửa các dự đoán không chắc chắn để đánh giá vẫn đến đúng hàng đợi xử lý.

**Acceptance Criteria:**
- [ ] Dashboard hiển thị danh sách đánh giá cần kiểm duyệt, sắp xếp độ tin cậy tăng dần.
- [ ] Quản trị viên có thể chấp nhận dự đoán hoặc chọn hàng đợi khác và nhập lý do tùy chọn.
- [ ] Khi sửa, đánh giá được chuyển sang hàng đợi mới và trạng thái chuyển thành `reviewed`.
- [ ] Quyết định kiểm duyệt được lưu trong lịch sử và có thể dùng làm dữ liệu gán nhãn cho lần huấn luyện sau.
- [ ] Verify in browser using dev-browser skill.

### US-007: Làm việc với hàng đợi nghiệp vụ
**Description:** Là nhân viên đơn vị xử lý, tôi muốn xem các đánh giá được giao cho hàng đợi của mình và cập nhật tiến độ xử lý.

**Acceptance Criteria:**
- [ ] Nhân viên chỉ xem được hàng đợi được phân quyền.
- [ ] Mỗi đánh giá hiển thị nội dung, nguồn dữ liệu, thời điểm nhận, nhãn lĩnh vực, nhãn cảm xúc, độ tin cậy và trạng thái.
- [ ] Có thể đổi trạng thái `new` → `in_progress` → `resolved` hoặc `closed`.
- [ ] Bộ lọc theo trạng thái, khoảng thời gian và độ tin cậy hoạt động chính xác.
- [ ] Verify in browser using dev-browser skill.

### US-008: Dashboard và báo cáo hai tác vụ NLP
**Description:** Là quản trị viên hoặc người nghiên cứu, tôi muốn xem hiệu quả định tuyến, phân loại lĩnh vực và phân tích cảm xúc để đánh giá hệ thống.

**Acceptance Criteria:**
- [ ] Dashboard hiển thị tổng đánh giá, số định tuyến tự động, số cần kiểm duyệt, tỷ lệ được hiệu chỉnh, phân bố theo hàng đợi và phân bố cảm xúc.
- [ ] Trang thực nghiệm hiển thị kết quả TF-IDF + SVM riêng cho tác vụ phân loại lĩnh vực và phân tích cảm xúc.
- [ ] Có confusion matrix riêng cho từng tác vụ của lần chạy được chọn.
- [ ] Có thể lọc báo cáo theo khoảng thời gian và xuất bảng số liệu CSV.
- [ ] Verify in browser using dev-browser skill.

## 5. Yêu cầu chức năng

- **FR-1:** Hệ thống phải quản lý năm nhãn hàng đợi nghiệp vụ: `customer_service`, `cards_accounts`, `digital_banking`, `credit_savings`, `payments_transfers`.
- **FR-2:** Hệ thống phải nhận đánh giá qua CSV, JSON và API; dataset cốt lõi là UTS2017_Bank, không yêu cầu kết nối Outlook/Gmail.
- **FR-3:** Hệ thống phải lưu nội dung đánh giá gốc, nội dung sau tiền xử lý, nguồn nạp, nhãn gốc, thời điểm nhận và trạng thái.
- **FR-4:** Hệ thống phải hỗ trợ gán nhãn thủ công, sửa nhãn và lưu lịch sử thay đổi nhãn.
- **FR-5:** Hệ thống phải sử dụng TF-IDF + SVM để huấn luyện, đánh giá và dự đoán cho cả hai tác vụ.
- **FR-6:** Hệ thống phải phân tích cảm xúc mỗi phản hồi thành `positive`, `negative` hoặc `neutral`; mỗi dự đoán phải gồm nhãn lĩnh vực, nhãn cảm xúc, điểm tin cậy cho từng tác vụ, mô hình/phiên bản mô hình và thời gian dự đoán.
- **FR-7:** Quản trị viên phải cấu hình được ngưỡng tự động định tuyến; giá trị mặc định là 0,80.
- **FR-8:** Đánh giá có điểm tin cậy dưới ngưỡng, đa chủ đề hoặc không ánh xạ được phải vào hàng đợi kiểm duyệt; đánh giá đạt ngưỡng phải vào hàng đợi nghiệp vụ tương ứng.
- **FR-9:** Hệ thống phải cho phép quản trị viên chấp nhận, sửa và định tuyến lại quyết định phân loại.
- **FR-10:** Hệ thống phải phân quyền tối thiểu theo ba vai trò đã nêu; nhân viên không được xem đánh giá của hàng đợi khác.
- **FR-11:** Dashboard phải có số liệu vận hành, phân bố cảm xúc và trang thực nghiệm có chỉ số cùng confusion matrix riêng cho hai tác vụ.
- **FR-12:** Hệ thống phải cung cấp API để nạp đánh giá, lấy kết quả dự đoán, xem hàng đợi và cập nhật trạng thái.
- **FR-13:** Hệ thống phải ghi audit log cho nạp đánh giá, dự đoán, định tuyến, thay đổi nhãn và thay đổi trạng thái.

## 6. Phi chức năng và kỹ thuật

- Giao diện và dữ liệu hiển thị tiếng Việt, mã hóa UTF-8.
- API nạp/dự đoán một đánh giá phải phản hồi dưới 3 giây ở tải demo (không tính thời gian huấn luyện mô hình).
- Huấn luyện TF-IDF + SVM chạy nền hoặc từ tác vụ quản trị; giao diện hiển thị trạng thái chạy và lỗi nếu có.
- Dataset phải được version hóa; kết quả thực nghiệm phải tái lập được bằng seed, cấu hình và phiên bản dữ liệu đã lưu.
- Thông tin định danh nhạy cảm trong dữ liệu demo phải được ẩn danh hóa; không đưa phản hồi khách hàng chưa được phép sử dụng vào kho mã nguồn.
- Hệ thống cần cơ chế xác thực, phân quyền và audit log tối thiểu phù hợp cho bản demo.
- Kiến trúc đề xuất: frontend dashboard, backend REST API, cơ sở dữ liệu quan hệ, kho tệp dataset/mô hình và mô-đun NLP tách biệt.

## 7. Cân nhắc thiết kế

- Màn hình tổng quan ưu tiên hiển thị số đánh giá mới, tỷ lệ tự động định tuyến, đánh giá cần kiểm duyệt và phân bố hàng đợi.
- Màu trạng thái phải có nhãn văn bản đi kèm, không chỉ dựa vào màu sắc.
- Trang chi tiết đánh giá phải luôn hiển thị nội dung gốc, nhãn gốc (nếu có), kết quả phân loại lĩnh vực, kết quả cảm xúc, lịch sử định tuyến và thao tác kiểm duyệt.
- Kết quả thực nghiệm TF-IDF + SVM cần ghi rõ dataset, cách chia dữ liệu, cấu hình TF-IDF và siêu tham số SVM để có giá trị học thuật.

## 8. Ngoài phạm vi

- Kết nối trực tiếp Outlook, Exchange, Gmail hoặc Google Workspace.
- Tự động gửi email hoặc phản hồi trực tiếp cho khách hàng.
- Tự động phân loại đa nhãn; các đánh giá có nhiều chủ đề sẽ được kiểm duyệt trong bản đầu.
- Tóm tắt đánh giá hoặc chatbot trả lời khách hàng.
- Hệ thống SLA, thông báo thời gian thực và tích hợp CRM/ERP.
- Triển khai production quy mô lớn hoặc cam kết độ chính xác cho dữ liệu doanh nghiệp thực.

## 9. Chỉ số thành công

- F1-macro của TF-IDF + SVM đạt tối thiểu 0,80 cho tác vụ phân loại lĩnh vực và 0,80 cho tác vụ phân tích cảm xúc trên tập test nội bộ.
- Tỷ lệ đánh giá được tự động định tuyến đạt ít nhất 70% với ngưỡng 0,80, đồng thời duy trì precision định tuyến tự động từ 90% trở lên.
- 100% đánh giá dưới ngưỡng, đa chủ đề hoặc lỗi mô hình xuất hiện trong hàng đợi kiểm duyệt.
- Quản trị viên hoàn tất thao tác chấp nhận hoặc sửa một đánh giá trong không quá 3 thao tác từ danh sách kiểm duyệt.
- Báo cáo thể hiện được kết quả TF-IDF + SVM của hai tác vụ, gồm các chỉ số và confusion matrix có thể xuất ra.

## 10. Dữ liệu và quy tắc ánh xạ

Nguồn dữ liệu cốt lõi là **UTS2017_Bank**, gồm các phản hồi/đánh giá khách hàng ngân hàng tiếng Việt đã ẩn danh, gán 14 nhãn lĩnh vực và ba nhãn cảm xúc `positive`, `negative`, `neutral`. Mô hình lĩnh vực dự đoán nhãn gốc hoặc nhãn hàng đợi đã ánh xạ; mô hình cảm xúc dự đoán độc lập ba nhãn cảm xúc. Bảng ánh xạ phải được version hóa và đưa vào báo cáo.

| Nhãn UTS2017_Bank | Hàng đợi định tuyến |
| --- | --- |
| `CUSTOMER_SUPPORT` | Chăm sóc khách hàng |
| `CARD`, `ACCOUNT` | Thẻ & Tài khoản |
| `INTERNET_BANKING`, `SECURITY` | Ngân hàng số |
| `LOAN`, `SAVING`, `INTEREST_RATE` | Tín dụng & Tiết kiệm |
| `MONEY_TRANSFER`, `PAYMENT`, `DISCOUNT` | Thanh toán & Chuyển tiền |
| `TRADEMARK`, `PROMOTION`, `OTHER` | Cần kiểm duyệt |

Ví dụ: “Tôi chuyển tiền nhưng ứng dụng báo lỗi” được phân loại `MONEY_TRANSFER` và định tuyến đến hàng đợi Thanh toán & Chuyển tiền. Phải báo cáo rõ số lượng mẫu sau ánh xạ và mức mất cân bằng của từng hàng đợi.

## 11. Định hướng và quyết định triển khai

- **Ngưỡng tin cậy:** Bản đầu dùng ngưỡng chung **0,80** cho tất cả hàng đợi nghiệp vụ. Sau thực nghiệm, nhóm sẽ phân tích hiệu quả theo từng hàng đợi; nếu cần, hệ thống có thể được mở rộng để cấu hình ngưỡng riêng cho từng hàng đợi.
- **Dataset:** **UTS2017_Bank** là dataset cốt lõi. Có thể bổ sung dữ liệu từ nguồn công khai khi cần; mọi dữ liệu phải được lọc, chuẩn hóa, ẩn danh và ánh xạ/gán nhãn về năm hàng đợi nghiệp vụ. Không tự tạo toàn bộ dataset; chỉ bổ sung dữ liệu thủ công khi nguồn công khai không đủ. Báo cáo phải nêu rõ nguồn gốc dữ liệu, giấy phép sử dụng và quy tắc ánh xạ nhãn.
- **Công nghệ:** Bản demo sử dụng **FastAPI** cho backend REST API, **React** cho frontend dashboard và **MySQL** cho cơ sở dữ liệu. Mô-đun NLP được tách biệt để hỗ trợ huấn luyện, đánh giá và triển khai mô hình.
- **Xác thực và phân quyền:** Bản demo có đăng nhập và phân quyền theo các vai trò `ADMIN`, `DEPARTMENT_STAFF` và `RESEARCHER`. Hệ thống sử dụng tài khoản demo; OAuth và tích hợp đăng nhập Microsoft/Google nằm ngoài phạm vi bản đầu.
