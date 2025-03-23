from transitions import Machine, MachineError
import time

class WashingMachine(object):
    def __init__(self):
        # Состояния автомата
        self.states = ['initial', 'filling', 'washing', 'draining', 'defect']
        
        # Переходы между состояниями
        self.transitions = [
            # Начало работы
            {'trigger': 'start', 'source': 'initial', 'dest': 'filling'},
            
            # Переход от залива к стирке
            {'trigger': 'water_full', 'source': 'filling', 'dest': 'washing'},
            
            # Переход от стирки к сливу (нормальный случай)
            {'trigger': 'timer_done', 'source': 'washing', 'dest': 'draining'},
            
            # Переход от стирки к дефекту (неисправный таймер)
            {'trigger': 'timer_fail', 'source': 'washing', 'dest': 'defect'},
            
            # Переход от слива к начальному состоянию
            {'trigger': 'water_empty', 'source': 'draining', 'dest': 'initial'},
            
            # Ремонт из состояния дефекта
            {'trigger': 'reset', 'source': 'defect', 'dest': 'initial'}
        ]
        
        # Инициализация машины состояний
        self.machine = Machine(
            model=self,
            states=self.states,
            transitions=self.transitions,
            initial='initial'
        )
        
        # Дополнительные параметры
        self.water_level = 0
        self.washing_time = 0
        self.is_timer_working = True
        self.max_water_level = 100
        self.max_washing_time = 30  # секунды
        
    def start(self):
        """Запуск стиральной машины"""
        if self.state == 'initial':
            print("Запуск стиральной машины...")
            self.water_level = 0
            self.washing_time = 0
            self.trigger('start')
        else:
            raise MachineError(f"Нельзя запустить стиральную машину из состояния {self.state}")
    
    def water_full(self):
        """Обработка сигнала заполнения бака"""
        if self.state == 'filling':
            if self.water_level >= self.max_water_level:
                print("Бак заполнен водой")
                self.trigger('water_full')
            else:
                print(f"Уровень воды: {self.water_level}%")
                self.water_level += 20
        else:
            raise MachineError(f"Нельзя обработать сигнал заполнения в состоянии {self.state}")
    
    def timer_done(self):
        """Обработка сигнала завершения стирки"""
        if self.state == 'washing':
            if self.is_timer_working:
                if self.washing_time >= self.max_washing_time:
                    print("Стирка завершена")
                    self.trigger('timer_done')
                else:
                    print(f"Время стирки: {self.washing_time} сек")
                    self.washing_time += 5
            else:
                raise MachineError("Таймер неисправен")
        else:
            raise MachineError(f"Нельзя обработать сигнал таймера в состоянии {self.state}")
    
    def timer_fail(self):
        """Обработка неисправности таймера"""
        if self.state == 'washing':
            print("Обнаружена неисправность таймера!")
            self.is_timer_working = False
            self.trigger('timer_fail')
        else:
            raise MachineError(f"Нельзя обработать неисправность таймера в состоянии {self.state}")
    
    def water_empty(self):
        """Обработка сигнала отсутствия воды"""
        if self.state == 'draining':
            if self.water_level <= 0:
                print("Бак пуст")
                self.trigger('water_empty')
            else:
                print(f"Уровень воды: {self.water_level}%")
                self.water_level -= 20
        else:
            raise MachineError(f"Нельзя обработать сигнал слива в состоянии {self.state}")
    
    def reset(self):
        """Ремонт стиральной машины"""
        if self.state == 'defect':
            print("Ремонт стиральной машины...")
            self.is_timer_working = True
            self.trigger('reset')
        else:
            raise MachineError(f"Нельзя выполнить ремонт в состоянии {self.state}")

def test_normal_cycle():
    """Тест нормального цикла работы стиральной машины"""
    washer = WashingMachine()
    print("\nТест нормального цикла работы:")
    print(f"Начальное состояние: {washer.state}")
    
    try:
        # Запуск
        washer.start()
        print(f"После нажатия 'Пуск': {washer.state}")
        
        # Заполнение бака
        while washer.state == 'filling':
            washer.water_full()
            time.sleep(1)
        
        # Стирка
        while washer.state == 'washing':
            washer.timer_done()
            time.sleep(1)
        
        # Слив воды
        while washer.state == 'draining':
            washer.water_empty()
            time.sleep(1)
        
        print(f"Конечное состояние: {washer.state}")
        
    except MachineError as error:
        print(f"Ошибка: {error}")

def test_defect_scenario():
    """Тест сценария с неисправностью таймера"""
    washer = WashingMachine()
    print("\nТест сценария с неисправностью:")
    print(f"Начальное состояние: {washer.state}")
    
    try:
        # Запуск
        washer.start()
        print(f"После нажатия 'Пуск': {washer.state}")
        
        # Заполнение бака
        while washer.state == 'filling':
            washer.water_full()
            time.sleep(1)
        
        # Стирка с неисправностью
        washer.timer_fail()
        print(f"После неисправности таймера: {washer.state}")
        
        # Попытка запуска из состояния дефекта
        try:
            washer.start()
            print("Ошибка: удалось запустить из состояния дефекта")
        except MachineError:
            print("Правильно: нельзя запустить из состояния дефекта")
        
        # Ремонт
        washer.reset()
        print(f"После ремонта: {washer.state}")
        
    except MachineError as error:
        print(f"Ошибка: {error}")

def test_invalid_transitions():
    """Тест некорректных переходов"""
    washer = WashingMachine()
    print("\nТест некорректных переходов:")
    
    try:
        # Попытка запуска из состояния дефекта
        washer.timer_fail()
        print("Ошибка: удалось вызвать timer_fail из начального состояния")
    except MachineError:
        print("Правильно: нельзя вызвать timer_fail из начального состояния")
    
    try:
        # Попытка ремонта из нормального состояния
        washer.start()
        washer.reset()
        print("Ошибка: удалось выполнить ремонт из нормального состояния")
    except MachineError:
        print("Правильно: нельзя выполнить ремонт из нормального состояния")

if __name__ == "__main__":
    test_normal_cycle()
    test_defect_scenario()
    test_invalid_transitions() 