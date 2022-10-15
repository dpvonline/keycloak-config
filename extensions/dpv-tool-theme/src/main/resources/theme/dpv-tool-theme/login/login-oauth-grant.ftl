<#import "template.ftl" as layout>
<#import "components/button/primary.ftl" as buttonPrimary>
<#import "components/button/secondary.ftl" as buttonSecondary>
<#import "components/input/primary.ftl" as inputPrimary>

<@layout.registrationLayout
bodyClass="oauth";
section>
    <#if section = "header">
        <#if client.attributes.logoUri??>
            <img src="${client.attributes.logoUri}"/>
        </#if>
        <p>
        <#if client.name?has_content>
            ${msg("oauthGrantTitle",advancedMsg(client.name))}
        <#else>
            ${msg("oauthGrantTitle",client.clientId)}
        </#if>
        </p>
    <#elseif section = "form">
        <div id="kc-oauth" class="content-area m-0 space-y-4">
            <h3>${msg("oauthGrantRequest")}</h3>
            <ul class="list-disc pl-6 py-2 space-y-2">
                <#if oauth.clientScopesRequested??>
                    <#list oauth.clientScopesRequested as clientScope>
                        <li>
                            <span><#if !clientScope.dynamicScopeParameter??>
                                        ${advancedMsg(clientScope.consentScreenText)}
                                    <#else>
                                        ${advancedMsg(clientScope.consentScreenText)}: <b>${clientScope.dynamicScopeParameter}</b>
                                </#if>
                            </span>
                        </li>
                    </#list>
                </#if>
            </ul>
            <#if client.attributes.policyUri?? || client.attributes.tosUri??>
                <h3>
                    <#if client.name?has_content>
                        ${msg("oauthGrantInformation",advancedMsg(client.name))}
                    <#else>
                        ${msg("oauthGrantInformation",client.clientId)}
                    </#if>
                    <#if client.attributes.tosUri??>
                        ${msg("oauthGrantReview")}
                        <a href="${client.attributes.tosUri}" target="_blank">${msg("oauthGrantTos")}</a>
                    </#if>
                    <#if client.attributes.policyUri??>
                        ${msg("oauthGrantReview")}
                          <@linkPrimary.kw href="${client.attributes.policyUri}" target="_blank">
                           ${msg("oauthGrantPolicy")}
                          </@linkPrimary.kw>
                    </#if>
                </h3>
            </#if>

            <form class="m-0 space-y-4" action="${url.oauthAction}" method="POST">
               <input type="hidden" name="code" value="${oauth.code}">
               <div class="${properties.kcFormGroupClass!}">
                    <div id="kc-form-options">
                        <div class="${properties.kcFormOptionsWrapperClass!}"/>
                    </div>
                    <div class="flex flex-col pt-4 space-y-2">
                        <@buttonPrimary.kw name="accept" id="kc-login" type="submit">
                          ${msg("doYes")}
                        </@buttonPrimary.kw>
                        <@buttonSecondary.kw name="cancel" id="kc-cancel" type="submit">
                          ${msg("doNo")}
                        </@buttonSecondary.kw>
                    </div>
                </div>
            </form>
            <div class="clearfix"/>
        </div>
    </#if>
</@layout.registrationLayout>