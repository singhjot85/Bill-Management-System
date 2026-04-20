(
    {
        amount: .amount | tonumber,
        currency: .currency,
        receipt: .external_reciept_number,
        partial_payment: false,
        notes: {
            description: .description,
            time_stamp: now
        }
    }
)
+
(
    if (.third_party_validation == true)
        then ({
                method: (.payments[0].payment_mode // null),
        })
        +
        (
            if .payments[0].payment_mode == "netbanking"
                then ({
                    bank_account: {
                        account_number: .account_number,
                        name: .name,
                        ifsc: .ifsc
                    }
                })
            # elif .method == "card"
            #     then ({
            #         card_details: {

            #         }
            #     })
            else null
            end
        )
    else null
    end
)
