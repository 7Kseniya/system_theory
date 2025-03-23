from transitions import Machine, MachineError
import time
import random

class Neuron(object):
    def __init__(self):
        # Состояния нейрона
        self.states = [
            'resting',           # Состояние покоя
            'depolarization',    # Деполяризация мембраны
            'repolarization',    # Реполяризация мембраны
            'refractory',        # Рефрактерный период
            'hyperpolarization', # Гиперполяризация
            'damaged',          # Повреждение нейрона
            'recovery'          # Восстановление после повреждения
        ]
        
        # Переходы между состояниями
        self.transitions = [
            # Основные переходы
            {'trigger': 'stimulate', 'source': 'resting', 'dest': 'depolarization'},
            {'trigger': 'na_channels_opened', 'source': 'depolarization', 'dest': 'repolarization'},
            {'trigger': 'k_channels_opened', 'source': 'repolarization', 'dest': 'refractory'},
            {'trigger': 'restore', 'source': 'refractory', 'dest': 'resting'},
            
            # Дополнительные переходы
            {'trigger': 'over_stimulate', 'source': 'depolarization', 'dest': 'hyperpolarization'},
            {'trigger': 'damage', 'source': ['depolarization', 'repolarization'], 'dest': 'damaged'},
            {'trigger': 'heal', 'source': 'damaged', 'dest': 'recovery'},
            {'trigger': 'complete_recovery', 'source': 'recovery', 'dest': 'resting'},
            
            # Переходы из гиперполяризации
            {'trigger': 'normalize', 'source': 'hyperpolarization', 'dest': 'resting'},
            {'trigger': 'damage', 'source': 'hyperpolarization', 'dest': 'damaged'}
        ]
        
        # Инициализация машины состояний
        self.machine = Machine(
            model=self,
            states=self.states,
            transitions=self.transitions,
            initial='resting'
        )
        
        # Дополнительные параметры
        self.membrane_potential = -70  # мВ
        self.threshold = -55          # мВ
        self.na_concentration = 1.0   # Относительная концентрация Na+
        self.k_concentration = 1.0    # Относительная концентрация K+
        self.refractory_time = 0      # мс
        self.health = 100            # Здоровье нейрона
        self.recovery_time = 0       # Время восстановления
        
    def stimulate(self):
        """Стимуляция нейрона"""
        if self.state == 'resting':
            print(f"Стимуляция нейрона (потенциал покоя: {self.membrane_potential} мВ)")
            self.membrane_potential += 20
            if self.membrane_potential >= self.threshold:
                print(f"Достигнут порог возбуждения: {self.membrane_potential} мВ")
                self.trigger('stimulate')
            else:
                print("Стимул ниже порога возбуждения")
        else:
            raise MachineError(f"Нельзя стимулировать нейрон в состоянии {self.state}")
    
    def over_stimulate(self):
        """Сверхсильная стимуляция"""
        if self.state == 'depolarization':
            if self.membrane_potential > 50:  # Сверхсильная деполяризация
                print(f"Сверхсильная стимуляция! Потенциал: {self.membrane_potential} мВ")
                self.membrane_potential = -90  # Гиперполяризация
                self.trigger('over_stimulate')
            else:
                print(f"Текущий потенциал: {self.membrane_potential} мВ")
        else:
            raise MachineError(f"Нельзя вызвать сверхстимуляцию в состоянии {self.state}")
    
    def na_channels_opened(self):
        """Открытие натриевых каналов"""
        if self.state == 'depolarization':
            if self.na_concentration > 0.2:
                self.membrane_potential += 40
                self.na_concentration -= 0.2
                print(f"Потенциал действия: {self.membrane_potential} мВ")
                if self.membrane_potential >= 30:
                    print("Достигнут пик потенциала действия")
                    self.trigger('na_channels_opened')
            else:
                print(f"Текущий потенциал: {self.membrane_potential} мВ")
        else:
            raise MachineError(f"Нельзя активировать Na+ каналы в состоянии {self.state}")
    
    def k_channels_opened(self):
        """Открытие калиевых каналов"""
        if self.state == 'repolarization':
            if self.k_concentration > 0.2:
                self.membrane_potential -= 30
                self.k_concentration -= 0.2
                print(f"Реполяризация: {self.membrane_potential} мВ")
                if self.membrane_potential <= -70:
                    print("Завершение реполяризации")
                    self.trigger('k_channels_opened')
            else:
                print(f"Текущий потенциал: {self.membrane_potential} мВ")
        else:
            raise MachineError(f"Нельзя активировать K+ каналы в состоянии {self.state}")
    
    def restore(self):
        """Восстановление концентраций ионов"""
        if self.state == 'refractory':
            if self.refractory_time < 20:
                self.refractory_time += 5
                print(f"Рефрактерный период: {self.refractory_time} мс")
            else:
                print("Восстановление концентраций ионов")
                self.membrane_potential = -70
                self.na_concentration = 1.0
                self.k_concentration = 1.0
                self.refractory_time = 0
                self.trigger('restore')
        else:
            raise MachineError(f"Нельзя восстановить концентрации в состоянии {self.state}")
    
    def damage(self):
        """Повреждение нейрона"""
        if self.state in ['depolarization', 'repolarization', 'hyperpolarization']:
            if random.random() < 0.3:  # 30% шанс повреждения
                print(f"Повреждение нейрона! Текущее здоровье: {self.health}")
                self.health -= 20
                if self.health <= 0:
                    print("Критическое повреждение!")
                    self.trigger('damage')
            else:
                print("Нейрон выдержал нагрузку")
        else:
            raise MachineError(f"Нельзя вызвать повреждение в состоянии {self.state}")
    
    def heal(self):
        """Лечение поврежденного нейрона"""
        if self.state == 'damaged':
            print("Начало лечения нейрона...")
            self.health = 50
            self.trigger('heal')
        else:
            raise MachineError(f"Нельзя лечить нейрон в состоянии {self.state}")
    
    def complete_recovery(self):
        """Завершение восстановления"""
        if self.state == 'recovery':
            if self.recovery_time < 30:
                self.recovery_time += 5
                self.health += 10
                print(f"Восстановление: {self.health}%")
            else:
                print("Нейрон полностью восстановлен")
                self.health = 100
                self.recovery_time = 0
                self.trigger('complete_recovery')
        else:
            raise MachineError(f"Нельзя завершить восстановление в состоянии {self.state}")
    
    def normalize(self):
        """Возврат к нормальному состоянию из гиперполяризации"""
        if self.state == 'hyperpolarization':
            print(f"Нормализация потенциала: {self.membrane_potential} мВ")
            self.membrane_potential += 5
            if self.membrane_potential >= -70:
                print("Возврат к потенциалу покоя")
                self.trigger('normalize')
        else:
            raise MachineError(f"Нельзя нормализовать потенциал в состоянии {self.state}")

def test_complex_scenario():
    """Тест сложного сценария с повреждением и восстановлением"""
    neuron = Neuron()
    print("\nТест сложного сценария:")
    print(f"Начальное состояние: {neuron.state}")
    
    try:
        # Запуск потенциала действия
        neuron.stimulate()
        print(f"После стимуляции: {neuron.state}")
        
        # Деполяризация с риском повреждения
        while neuron.state == 'depolarization':
            neuron.na_channels_opened()
            neuron.damage()  # Попытка повреждения
            time.sleep(0.5)
        
        # Реполяризация
        while neuron.state == 'repolarization':
            neuron.k_channels_opened()
            neuron.damage()  # Попытка повреждения
            time.sleep(0.5)
        
        # Рефрактерный период
        while neuron.state == 'refractory':
            neuron.restore()
            time.sleep(0.5)
        
        print(f"Конечное состояние: {neuron.state}")
        
    except MachineError as error:
        print(f"Ошибка: {error}")

def test_damage_recovery():
    """Тест сценария повреждения и восстановления"""
    neuron = Neuron()
    print("\nТест повреждения и восстановления:")
    print(f"Начальное состояние: {neuron.state}")
    
    try:
        # Стимуляция
        neuron.stimulate()
        
        # Попытка повреждения
        neuron.damage()
        
        # Если повреждение произошло
        if neuron.state == 'damaged':
            print("Начало процесса восстановления")
            neuron.heal()
            
            # Восстановление
            while neuron.state == 'recovery':
                neuron.complete_recovery()
                time.sleep(0.5)
        
        print(f"Конечное состояние: {neuron.state}")
        
    except MachineError as error:
        print(f"Ошибка: {error}")

def test_complex_invalid_transitions():
    """Тест сложных некорректных переходов"""
    neuron = Neuron()
    print("\nТест сложных некорректных переходов:")
    
    # Тест 1: Попытка лечения здорового нейрона
    try:
        neuron.heal()
        print("Ошибка: удалось лечить здоровый нейрон")
    except MachineError:
        print("Правильно: нельзя лечить здоровый нейрон")
    
    # Тест 2: Попытка сверхстимуляции в состоянии покоя
    try:
        neuron.over_stimulate()
        print("Ошибка: удалось вызвать сверхстимуляцию из состояния покоя")
    except MachineError:
        print("Правильно: нельзя вызвать сверхстимуляцию из состояния покоя")
    
    # Тест 3: Попытка нормализации в состоянии покоя
    try:
        neuron.normalize()
        print("Ошибка: удалось нормализовать потенциал в состоянии покоя")
    except MachineError:
        print("Правильно: нельзя нормализовать потенциал в состоянии покоя")
    
    # Тест 4: Попытка завершения восстановления без лечения
    try:
        neuron.complete_recovery()
        print("Ошибка: удалось завершить восстановление без лечения")
    except MachineError:
        print("Правильно: нельзя завершить восстановление без лечения")
    
    # Тест 5: Попытка повреждения в состоянии покоя
    try:
        neuron.damage()
        print("Ошибка: удалось повредить нейрон в состоянии покоя")
    except MachineError:
        print("Правильно: нельзя повредить нейрон в состоянии покоя")

if __name__ == "__main__":
    test_complex_scenario()
    test_damage_recovery()
    test_complex_invalid_transitions() 