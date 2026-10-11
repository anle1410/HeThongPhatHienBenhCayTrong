import 'dart:io';
import 'dart:typed_data';
import 'dart:math' as math;
import 'package:tflite_flutter/tflite_flutter.dart';
import 'package:image/image.dart' as img;

class AgriVisionService {
  Interpreter? _interpreter;
  List<String>? _labels;

  bool get isModelLoaded => _interpreter != null;

  Future<void> loadModel() async {
    try {
      // Nhớ trỏ đúng tên file TFLite mới nhé!
      _interpreter = await Interpreter.fromAsset('assets/models/agrivision_tf_model.tflite');
      
      _labels = [
        'Ngô - Đốm lá xám (Cercospora)', 
        'Ngô - Rỉ sắt (Common rust)',
        'Ngô - Cháy lá (Northern Leaf Blight)',
        'Ngô - Khỏe mạnh',
        'Ớt chuông - Đốm vi khuẩn',
        'Ớt chuông - Khỏe mạnh',
        'Khoai tây - Bệnh mốc sương sớm',
        'Khoai tây - Bệnh mốc sương mai',
        'Khoai tây - Khỏe mạnh',
        'Cà chua - Đốm vi khuẩn',
        'Cà chua - Bệnh mốc sương sớm',
        'Cà chua - Bệnh mốc sương mai',
        'Cà chua - Nấm mốc lá',
        'Cà chua - Đốm lá Septoria',
        'Cà chua - Nhện đỏ',
        'Cà chua - Đốm vòng (Target Spot)',
        'Cà chua - Xoăn lá vàng do Virus',
        'Cà chua - Khảm lá do Virus',
        'Cà chua - Khỏe mạnh'
      ];
      print('>>> Đã nạp thành công bộ não TensorFlow AgriVision!');
    } catch (e) {
      print('>>> Lỗi khi nạp model: $e');
    }
  }

  Future<Map<String, dynamic>?> predict(String imagePath) async {
    if (_interpreter == null) return null;

    File imageFile = File(imagePath);
    img.Image? originalImage = img.decodeImage(imageFile.readAsBytesSync());
    if (originalImage == null) return null;

    // 1. Tiền xử lý ảnh (Cực kỳ đơn giản)
    Float32List inputBytes = preprocessImage(originalImage);
    var inputShape = _interpreter!.getInputTensor(0).shape; // Sẽ là [1, 224, 224, 3]
    var input = inputBytes.reshape(inputShape);
    
    var outputShape = _interpreter!.getOutputTensor(0).shape; // Sẽ là [1, 19]
    var output = List.filled(outputShape.reduce((a, b) => a * b), 0.0).reshape(outputShape);

    // 2. Chạy suy luận
    _interpreter!.run(input, output);

    // 3. Lấy kết quả (Vì đã có Softmax trong model, đây CHÍNH LÀ % xác suất luôn)
    List<double> probabilities = (output[0] as List).cast<double>();

    double maxProb = 0.0;
    int maxIndex = -1;
    
    for (int i = 0; i < probabilities.length; i++) {
      if (probabilities[i] > maxProb) {
        maxProb = probabilities[i];
        maxIndex = i;
      }
    }

    return {
      'disease': _labels![maxIndex],
      'confidence': (maxProb * 100).toStringAsFixed(2),
    };
  }

  /// Hàm tiền xử lý: Chỉ cần Cắt vuông (Crop) và Thu nhỏ (Resize).
  /// KHÔNG CẦN Normalize vì EfficientNet của TensorFlow tự động làm!
  Float32List preprocessImage(img.Image originalImage) {
    // Cắt ảnh thành hình vuông ở chính giữa
    int size = math.min(originalImage.width, originalImage.height);
    int offsetX = (originalImage.width - size) ~/ 2;
    int offsetY = (originalImage.height - size) ~/ 2;
    img.Image squareImage = img.copyCrop(originalImage, x: offsetX, y: offsetY, width: size, height: size);
    
    // Thu nhỏ về 224x224
    img.Image resizedImage = img.copyResize(squareImage, width: 224, height: 224);

    var float32Data = Float32List(1 * 224 * 224 * 3);
    int pixelIndex = 0;

    // Băm ảnh theo chuẩn NHWC (Đỏ-Xanh-Xanh xen kẽ)
    for (int y = 0; y < 224; y++) {
      for (int x = 0; x < 224; x++) {
        var pixel = resizedImage.getPixel(x, y);
        // Truyền thẳng giá trị pixel thô (0 - 255) vào mảng
        float32Data[pixelIndex++] = pixel.r.toDouble();
        float32Data[pixelIndex++] = pixel.g.toDouble();
        float32Data[pixelIndex++] = pixel.b.toDouble();
      }
    }
    return float32Data;
  }
}