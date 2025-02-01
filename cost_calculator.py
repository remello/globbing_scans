class CostCalculator:
    def __init__(self):
        self._weight_cost_modifier = 1470

    @property
    def weight_cost_modifier(self):
        return self._weight_cost_modifier

    @weight_cost_modifier.setter
    def weight_cost_modifier(self, value):
        try:
            new_value = float(value)
            if new_value <= 0:
                raise ValueError("Модификатор стоимости должен быть положительным числом")
            self._weight_cost_modifier = new_value
        except ValueError as e:
            raise ValueError("Неверный формат модификатора стоимости") from e

    def calculate_cost(self, weight_str):
        """
        Рассчитывает стоимость на основе веса
        
        Args:
            weight_str: Строка с весом (например, "1,5 кг")
            
        Returns:
            float: Рассчитанная стоимость
        """
        try:
            weight_value = float(weight_str.split()[0].replace(",", "."))
            return weight_value * self.weight_cost_modifier
        except (ValueError, IndexError) as e:
            raise ValueError("Неверный формат веса") from e
