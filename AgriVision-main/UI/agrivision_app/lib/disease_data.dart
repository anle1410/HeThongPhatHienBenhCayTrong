class DiseaseData {
  static const Map<String, String> treatments = {
    'Ngô - Đốm lá xám (Cercospora)': 'Ngắt bỏ lá bệnh thưa gốc. Phun thuốc gốc Đồng (Copper Oxychloride) hoặc Mancozeb theo liều lượng bao bì. Luân canh cây trồng khác họ.',
    'Ngô - Rỉ sắt (Common rust)': 'Sử dụng các loại thuốc trừ nấm chứa hoạt chất Propiconazole hoặc Tebuconazole. Dọn sạch tàn dư thực vật sau khi thu hoạch.',
    'Khoai tây - Bệnh mốc sương mai': 'Bệnh lây lan rất nhanh khi ẩm độ cao. Cần phun phòng bằng Mancozeb hoặc Metalaxyl. Cắt bỏ tiêu hủy ngay cây chớm bệnh.',
    // Add more treatments
  };

  static String getTreatment(String diseaseName) {
    return treatments[diseaseName] ?? 'Khuyến nghị: Theo dõi thêm tiến triển của bệnh và mang mẫu lá đến trạm Khuyến nông địa phương để được tư vấn chính xác.';
  }
}