import math

# 年化利率
annual_rate = 0.0546

# 使用复利公式计算每月利率
monthly_rate = (1 + annual_rate) ** (1/12) - 1

# 输出结果
print(f"每月利率: {monthly_rate * 100:.4f}%")