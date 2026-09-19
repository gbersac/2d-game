extends Node

signal money_changed(amount: int)

var money: int = 0


func add(amount: int) -> void:
	money += amount
	money_changed.emit(money)
