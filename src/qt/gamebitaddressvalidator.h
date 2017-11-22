// Copyright (c) 2011-2014 The GameBit Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef GameBit_QT_GameBitADDRESSVALIDATOR_H
#define GameBit_QT_GameBitADDRESSVALIDATOR_H

#include <QValidator>

/** Base58 entry widget validator, checks for valid characters and
 * removes some whitespace.
 */
class GameBitAddressEntryValidator : public QValidator
{
    Q_OBJECT

public:
    explicit GameBitAddressEntryValidator(QObject *parent);

    State validate(QString &input, int &pos) const;
};

/** GameBit address widget validator, checks for a valid GameBit address.
 */
class GameBitAddressCheckValidator : public QValidator
{
    Q_OBJECT

public:
    explicit GameBitAddressCheckValidator(QObject *parent);

    State validate(QString &input, int &pos) const;
};

#endif // GameBit_QT_GameBitADDRESSVALIDATOR_H
