<html>
<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
    <style type="text/css">
    table {
        page-break-after:auto;
        font-size:13px;
        border:1px solid black;
        position:fixed;
        top:350px;
       }

    div.logo
        {
        position:fixed;
        top:73px;
        left:20px;
        width:30px;
        height:5px;
        }
    div.barcode
        {
        position:fixed;
        left:630px;
        top:100px;
        }

    div.expediteur
        {
        position:fixed;
        top:100px;
        width:600px;
        height:120px;
        padding:2px;
        border:1px solid black;
        margin:0px;
        font-size:14px;
        }
    div.reference_douane
        {
        position:fixed;
        top:100px;
        left:300px;
        width:302px;
        height:10px;
        padding:5px;
        border:1px solid black;
        margin:0px;
        font-size:12px;
        }
    div.destinataire
        {
        position:fixed;
        top:225px;
        width:600px;
        height:120px;
        padding:2px;
        border:1px solid black;
        margin:0px;
        font-size:14px;
        }
    div.reference_importateur
        {
        position:fixed;
        top:235px;
        left:614px;
        width:360px;
        height:55px;
        padding:2px;
        border:1px solid black;
        margin:0px;
        font-size:13px
        }
    div.coordonnee_importateur
        {
        position:fixed;
        top:295px;
        left:614px;
        width:360px;
        height:40px;
        padding:2px;
        border:1px solid black;
        margin:0px;
        font-size:13px
        }
    div.envois_commerciaux
        {
        position:fixed;
        top:330px;
        left:614px;
        width:360px;
        height:15px;
        padding:2px;
        border:1px solid black;
        margin:0px;
        background: lightgrey;
        font-size:13px;
        text-align:center;
        }
    .categorie_envoi
        {
        position:absolute;
        left:-1px;
        width:600px;
        height:200px;
        padding:2px;
        border-left:1px solid black;
        border-right:1px solid black;
        border-bottom:1px solid black;
        margin:0px;
        font-size:13px;
        }
    .bureau
        {
        position:absolute;
        left:606px;
        width:360px;
        height:200px;
        padding:2px;
        border-right:1px solid black;
        border-bottom:1px solid black;
        margin:0px;
        font-size:13px;
        }
    div.carre{
        width:10px;
        height:10px;
        border:1px solid black;
        }
    div.gdcarre{
        width:15px;
        height:15px;
        border:1px solid black;
        position:absolute;
        left:1px;
        top:1px;
        }
    div.equerre{
        width:199px;
        height:30px;
        border-bottom:1px solid black;
        border-right:1px solid black
        }
    div.traith{
        width:200px;
        height:30px;
        border-bottom:1px solid black;
        }
    div.traitv{
        width:199px;
        height:30px;
        border-right:1px solid black;
        }
    .licence
        {
        position:absolute;
        top:142px;
        left:-1px;
        width:199px;
        height:30px;
        padding:2px;
        margin:0px;
        font-size:12px;
        text-align:center;
        }
    .certificat
        {
        position:absolute;
        left:200px;
        top:142px;
        width:199px;
        height:30px;
        padding:2px;
        margin:0px;
        font-size:12px;
        text-align:center;
        }
    .facture
        {
        position:absolute;
        left:400px;
        top:142px;
        width:199px;
        height:30px;
        padding:2px;
        margin:0px;
        font-size:12px;
        text-align:center;
        }
    div.cn11
        {
        position:absolute;
        top:1100px;
        width:965px;
        height:220px;
        padding:2px;
        border:1px solid black;
        margin:0px;
        font-size:13px;
        }
    div.header_cn11
        {
        position:absolute;
        top:0px;
        left:0px;
        width:965px;
        height:20px;
        padding:2px;
        border:1px solid black;
        margin:0px;
        font-size:16px;
        background:lightgrey;
        text-align:center;
        }
     hr.cn11
        {
        width:965px;
        border:1px solid black;
        }
    .rectangle1
        {
        position:absolute;
        left:600px;
        top:45px;
        width:80px;
        height:20px;
        border:1px solid black;
        }
    .rectangle2
        {
        position:absolute;
        left:600px;
        top:65px;
        width:80px;
        height:20px;
        border:1px solid black;
        }
    .rectangle3
        {
        position:absolute;
        left:600px;
        top:85px;
        width:80px;
        height:20px;
        border:1px solid black;
        }
    .entete_tab {text-align:center; background: lightgrey;}

    .encadre1 {border-bottom:1px solid black; border-right:1px solid black;}

    .encadre2 {border-bottom:1px solid black;}

    .encadre3 {border-right:1px solid black;}

    .left_posA {position:absolute; left:5px}

    .left_posB {font-weight:bold; position:absolute; left:75px}

    .left_posC {position:absolute; left:150px}

    .left_posD {position:absolute; left:220px}


    </style>
</head>
<body style="width:900px; height:1250px;">
<%
from datetime import date

def main_condition(picking):
    if ((picking.carrier_code in ['7Q','8Q']) \
            and (picking.partner_id.country_id.code in ['GP','MQ','GY','RE','YT'])) \
        or ((picking.carrier_code in ['8V','8L']) \
            and (picking.partner_id.country_id.code == 'AD')):
        return True
    return False

def product_price(move):
    if move.sale_line_id:
        return move.sale_line_id.price_unit
    else:
        return move.product_id.list_price

def search_ftd_option(picking):
    for opt in picking.option_ids:
        if opt.tmpl_option_id.code == 'FTD':
            return True
    return False

%>
    %for picking in objects:
<!--   CN23   -->
    <div class="logo">${helper.embed_logo_by_name('LAPOSTE')}</div>
    <span style="position:fixed; left:420px; top:75px"><b>FRANCE</b></span>
    <span style="position:fixed; left:660px; top:75px"><b>DECLARATION EN DOUANE CN23</b></span>
        %if main_condition(picking):
    <div class="barcode">${helper.embed_image("png", picking.get_128_barcode(), height=100)}</div>
    <span style="position:fixed; left:740px; top:210px">${picking.carrier_tracking_ref}</span>
        %endif
    <div class="expediteur">
        <div class="reference_douane">Référence en douane</div>
        <span><b>EXPEDITEUR</b></span>
        <br/>
        <span class="left_posA">Société</span>
        <span class="left_posB"">${company.partner_id.name}</span>
        <br/>
        <span class="left_posA">Adresse</span>
        <span class="left_posB">${company.partner_id and company.partner_id.street or ''}</span>
        <br/>
        <span class="left_posB">${company.partner_id and company.partner_id.street2 or ''}</span>
        <br/>
        <span class="left_posA">C.P.</span>
        <span class="left_posB">${company.partner_id.zip or ''}</span>
        <span class="left_posC">VILLE</span>
        <span class="left_posD"><b>${company.partner_id.city or ''}</b></span>
        <br/>
        <span style="font-weight:bold">${company.partner_id.country_id.name or ''}</span>
    </div>
    <div class="destinataire">
        <span style="font-weight:bold">DESTINATAIRE</span><br/>
        <span class="left_posA">Société</span>
        <span class="left_posB">${picking.partner_id.name}</span>
        <br/>
        <span class="left_posA">Adresse</span>
        <span class="left_posB">${picking.partner_id.street or ''}</span>
        <br/>
        <span class="left_posB">${picking.partner_id.street2 or ''}</span>
        <br/>
        <span class="left_posA">C.P.</span>
        <span class="left_posB">${picking.partner_id.zip or ''}</span>
        <span class="left_posC">VILLE</span>
        <span class="left_posD"><b>${picking.partner_id.city or ''}</b></span>
        <br/>
        <span><b>${picking.partner_id.country_id.name or ''}</b></span>
    </div>
    <div class="reference_importateur">
        Référence de l'importateur (si elle existe) (code fiscal/n° de TVA/ code de l'importateur) (facultatif)
    </div>
    <div class="coordonnee_importateur">
        N° de téléphone/fax/e-mail de l'importateur (si connu)
    </div>
    <div class="envois_commerciaux">
        Pour les envois commerciaux seulement
    </div>
    <% number_of_packages = 0 %>
    <table>
        <thead class="entete_tab">
            <tr>
                <th class="encadre1" style="width:340px; text-align:left;"> Description détaillée du contenu</th>
                <th class="encadre1" style="width:55px;">Qté</th>
                <th class="encadre1" style="width:110px;">Poids net (kg)</th>
                <th class="encadre1" style="width:80px;">Valeur EUR</th>
                <th class="encadre1" style="width:125px;">N° tarifaire</th>
                <th class="encadre2" style="width:229px;">Pays d'origine</th>
            </tr>
        </thead>
        <tbody>
        %for move in picking.move_lines:
            <tr>
                <td class="encadre1" style="text-align:left;">${move.name}</td>
                <td class="encadre1" style="text-align:center;">${move.product_qty}</td>
                <td class="encadre1" style="text-align:right;">${move.weight}</td>
                <td class="encadre1" style="text-align:right;">${product_price(move) * move.product_qty}</td>
                <td class="encadre1" style="text-align:center;">${move.product_id.intrastat_id.name or ''}</td>
                <td class="encadre2" style="text-align:left;">${company.partner_id.country_id and company.partner_id.country_id.name or ''}</td>
            </tr>
            <% number_of_packages += move.product_qty %>
        %endfor
            <tr>
                <td class="encadre3"></td>
                <td class="encadre3" style="text-align:center;">Total:</td>
                <td class="encadre3" style="text-align:right;">${number_of_packages}</td>
                <td class="encadre3" style="text-align:right;">${picking.sale_id.amount_untaxed or 0}</td>
                <td> Frais de port/Frais</td>
                <td style ="position:absolute; left:850px; "> ${picking.get_shipping_cost()}  EUR</td>
            </tr>

            <tr>
                <td class="categorie_envoi">
                        <span class="left_posA"><b>Catégorie de l'envoi</b></span>
                        <span style="font-weight:bold; position:absolute; left:200px;">Explication:</span>
                        <br/>
                        <div class="carre left_posA"></div>
                        <span style="position:absolute; left:25px">Cadeau</span>
                        <div class="carre" style="position:absolute; left:120px"></div>
                        <span style="position:absolute; left:140px">Echantillon commercial</span>
                        <div class="carre" style="position:absolute; left:320px"></div>
                        <span style="position:absolute; left:320px; top:15px; font-size:16px;">X</span>
                        <span style="position:absolute; left:340px;">Envoi commercial</span>
                        <br/>
                        <div class="carre left_posA"></div>
                        <span style="position:absolute; left:25px">Document</span>
                        <div class="carre" style="position:absolute; left:120px"></div>
                        <span style="position:absolute; left:140px">Retour de marchandise</span>
                        <div class="carre" style="position:absolute; left:320px"></div>
                        <span style="position:absolute; left:340px">Autre</span>
                        <br/>
                        <hr style="width:965px; border:1px solid black;">
                        <span style="font-weight:bold">Observations:(p.ex marchandise soumise à la quarantaine/à des contrôles sanitaires,
                        phytosanitaires ou à d'autres restrictions)</span><br/>
                        <br/>
                        <br/>
                        <hr style="width:600px; border:1px solid black;">
                        <span class="licence">
                            <div class="equerre">
                                <div class="gdcarre"></div>
                                Licence<br/>
                                N° de la/des licences
                            </div>
                        </span>
                        <span class="certificat">
                            <div class="equerre">
                                <div class="gdcarre"></div>
                                Certificat<br/>
                                N° du/des certificats
                            </div>
                        </span>
                        <span class="facture">
                            <div class="traith">
                                <div class="gdcarre"></div>
                                Facture<br/>
                                N° de la facture
                            </div>
                        </span>
                        <div class="traitv" style="position:absolute; left:1px; top:174px;"></div>
                        <div class="traitv" style="position:absolute; left:202px; top:174px;"></div>
                </td>
                <td class="bureau">
                        Bureau d'origine/Date de dépôt
                        <br/>
                        <br/>
                        <span style="position:absolute; left:75px">${company.colipostefr_support_city or ''} ${formatLang(str(date.today()), date=True)}</span>
                        <br/>
                        <br/>
                        Je certifie que les renseignements donnés dans la présente déclaration en douane sont exacts
                        et que cet envoi ne contient aucun objet dangereux ou interdit par la législation ou la réglementation
                        postale ou douanière.
                        <br/>
                        <br/>
                        Date et signature de l'expéditeur
                </td>
            </tr>
        </tbody>
    </table>
<!--   CN11   -->
        %if ((picking.carrier_code == '7Q') \
            and (picking.partner_id.country_id.code in ['GP','MQ','GY','RE','YT']) \
            and search_ftd_option(picking)):
        <div class="cn11">
            <div class="header_cn11">FORMULAIRE FRANC DE TAXES ET DROITS (CN11)</div>
            <br/>
            <br/>
            <br/>
            Droits de douane
            <div class="rectangle1"></div>
            <br/>
            Taxe de présentation en douane
            <div class="rectangle2"></div>
            <br/>
            <span style="font-weight:bold">Total TTC</span>
            <div class="rectangle3"></div>
            <br/>
            <br/>
            <hr class="cn11"/>
            L'envoi doit être remis franc de taxes et de
            <span style="position:absolute; left:600px;">Timbre à date du bureau destinataire</span>
            <br/>
            droits que je m'engage à payer.
            <br/>
            <br/>
            Signature de l'expéditeur
            <br/>
            <span style="position:absolute; left:620px;">FORMULAIRE A RETOURNER AU BUREAU D'ECHANGE</span>
        </div>
        %endif
    %endfor
</body>
</html>
