package main

import (
	"github.com/tyler-smith/go-bip39"
)
func GenerateMnemonic()(string,error){
	entropy,err:=bip39.NewEntropy(128)
	if err!=nil{
		return "",err
	}
	mnemonic,err:=bip39.NewMnemonic(entropy)
	return mnemonic,err
}
func ValidateMnemonic(mnemonic string)bool  {
	return bip39.IsMnemonicValid(mnemonic)
}